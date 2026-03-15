"""Unit tests for the mission planner and behaviour tree nodes.

Tests state machine transitions, safety checks, BT node logic,
and patrol generation without a running ROS2 system.
"""

import math
import time
import pytest
from unittest.mock import MagicMock

from rover_autonomy.mission_planner import (
    MissionPlannerNode,
    BTStatus,
    SequenceNode,
    FallbackNode,
    RepeatNode,
    ConditionNode,
    ActionNode,
)


@pytest.fixture
def planner():
    """Create a MissionPlannerNode with default parameters."""
    return MissionPlannerNode()


# ===== BTStatus enum =====

class TestBTStatus:
    def test_status_values(self):
        assert BTStatus.SUCCESS.value == 'success'
        assert BTStatus.FAILURE.value == 'failure'
        assert BTStatus.RUNNING.value == 'running'


# ===== SequenceNode =====

class TestSequenceNode:
    """Sequence ticks children in order, fails on first failure."""

    def test_all_success(self):
        seq = SequenceNode('test_seq')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.SUCCESS
        child2 = MagicMock()
        child2.tick.return_value = BTStatus.SUCCESS
        seq.children = [child1, child2]

        result = seq.tick({})
        assert result == BTStatus.SUCCESS

    def test_first_failure_stops(self):
        seq = SequenceNode('test_seq')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.FAILURE
        child2 = MagicMock()
        child2.tick.return_value = BTStatus.SUCCESS
        seq.children = [child1, child2]

        result = seq.tick({})
        assert result == BTStatus.FAILURE
        child2.tick.assert_not_called()

    def test_running_pauses(self):
        seq = SequenceNode('test_seq')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.RUNNING
        seq.children = [child1]

        result = seq.tick({})
        assert result == BTStatus.RUNNING

    def test_empty_sequence_succeeds(self):
        seq = SequenceNode('empty')
        result = seq.tick({})
        assert result == BTStatus.SUCCESS


# ===== FallbackNode =====

class TestFallbackNode:
    """Fallback ticks children in order, succeeds on first success."""

    def test_first_success_stops(self):
        fb = FallbackNode('test_fb')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.SUCCESS
        child2 = MagicMock()
        child2.tick.return_value = BTStatus.FAILURE
        fb.children = [child1, child2]

        result = fb.tick({})
        assert result == BTStatus.SUCCESS
        child2.tick.assert_not_called()

    def test_all_failure(self):
        fb = FallbackNode('test_fb')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.FAILURE
        child2 = MagicMock()
        child2.tick.return_value = BTStatus.FAILURE
        fb.children = [child1, child2]

        result = fb.tick({})
        assert result == BTStatus.FAILURE

    def test_running_pauses(self):
        fb = FallbackNode('test_fb')
        child1 = MagicMock()
        child1.tick.return_value = BTStatus.RUNNING
        fb.children = [child1]

        result = fb.tick({})
        assert result == BTStatus.RUNNING

    def test_empty_fallback_fails(self):
        fb = FallbackNode('empty')
        result = fb.tick({})
        assert result == BTStatus.FAILURE


# ===== RepeatNode =====

class TestRepeatNode:
    """Repeat ticks its child N times."""

    def test_repeat_finite(self):
        rep = RepeatNode('rep', count=3)
        child = MagicMock()
        child.tick.return_value = BTStatus.SUCCESS
        rep.children = [child]

        # First two ticks should return RUNNING (more iterations needed)
        assert rep.tick({}) == BTStatus.RUNNING
        assert rep.tick({}) == BTStatus.RUNNING
        # Third tick should return SUCCESS (count reached)
        assert rep.tick({}) == BTStatus.SUCCESS

    def test_repeat_infinite_never_succeeds(self):
        rep = RepeatNode('rep', count=-1)
        child = MagicMock()
        child.tick.return_value = BTStatus.SUCCESS
        rep.children = [child]

        # Should always return RUNNING
        for _ in range(100):
            assert rep.tick({}) == BTStatus.RUNNING

    def test_repeat_no_children_fails(self):
        rep = RepeatNode('rep', count=3)
        assert rep.tick({}) == BTStatus.FAILURE

    def test_repeat_child_running_propagates(self):
        rep = RepeatNode('rep', count=3)
        child = MagicMock()
        child.tick.return_value = BTStatus.RUNNING
        rep.children = [child]

        assert rep.tick({}) == BTStatus.RUNNING
        # Iterations should not increment when child is running
        assert rep.iterations == 0


# ===== ConditionNode =====

class TestConditionNode:
    """Condition checks a blackboard key."""

    def test_condition_true(self):
        cond = ConditionNode('check', 'battery_ok', expected=True)
        result = cond.tick({'battery_ok': True})
        assert result == BTStatus.SUCCESS

    def test_condition_false(self):
        cond = ConditionNode('check', 'battery_ok', expected=True)
        result = cond.tick({'battery_ok': False})
        assert result == BTStatus.FAILURE

    def test_condition_missing_key_fails(self):
        cond = ConditionNode('check', 'nonexistent', expected=True)
        result = cond.tick({})
        assert result == BTStatus.FAILURE

    def test_condition_expected_false(self):
        cond = ConditionNode('check', 'estop_active', expected=False)
        result = cond.tick({'estop_active': False})
        assert result == BTStatus.SUCCESS


# ===== ActionNode =====

class TestActionNode:
    """Action delegates to handler in blackboard."""

    def test_action_calls_handler(self):
        handler = MagicMock(return_value=BTStatus.SUCCESS)
        bb = {'_action_test': handler}
        action = ActionNode('do_test', 'test', {'key': 'value'})

        result = action.tick(bb)
        assert result == BTStatus.SUCCESS
        handler.assert_called_once_with({'key': 'value'}, bb)

    def test_action_missing_handler_fails(self):
        action = ActionNode('do_test', 'nonexistent')
        result = action.tick({})
        assert result == BTStatus.FAILURE


# ===== Mission state transitions =====

class TestMissionStateTransitions:
    """Test activate/deactivate and mission lifecycle."""

    def test_initial_state_inactive(self, planner):
        assert planner.active is False
        assert planner.current_bt is None

    def test_activate_sets_active(self, planner):
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)
        assert planner.active is True

    def test_deactivate_sets_inactive(self, planner):
        # Activate first
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)

        # Then deactivate
        msg.data = False
        planner.activate_callback(msg)
        assert planner.active is False

    def test_activate_loads_default_bt(self, planner):
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)
        # Should have loaded the fallback simple patrol BT
        assert planner.current_bt is not None

    def test_double_activate_no_effect(self, planner):
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)
        bt1 = planner.current_bt

        planner.activate_callback(msg)
        bt2 = planner.current_bt
        # Should be the same BT, not re-loaded
        assert bt1 is bt2

    def test_tick_skipped_when_inactive(self, planner):
        """tick() should be a no-op when not active."""
        planner.active = False
        planner.tick()  # Should not crash


# ===== Mission abort on E-stop (critical battery) =====

class TestMissionAbort:
    """Test safety abort conditions."""

    def test_abort_on_critical_battery(self, planner):
        """Battery < 10% should deactivate the mission."""
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)
        assert planner.active is True

        planner.battery_pct = 5
        planner.current_pose = (1.0, 1.0, 0.0)
        planner.tick()
        assert planner.active is False

    def test_battery_above_critical_continues(self, planner):
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)

        planner.battery_pct = 50
        planner.tick()
        assert planner.active is True

    def test_battery_exactly_10_continues(self, planner):
        """Boundary: 10% should NOT trigger abort (< 10 is the check)."""
        msg = MagicMock()
        msg.data = True
        planner.activate_callback(msg)

        planner.battery_pct = 10
        planner.tick()
        assert planner.active is True


# ===== Battery check action =====

class TestBatteryCheckAction:
    """Test the _action_check_battery handler."""

    def test_battery_ok(self, planner):
        bb = {'battery_pct': 80}
        result = planner._action_check_battery({}, bb)
        assert result == BTStatus.SUCCESS

    def test_battery_low(self, planner):
        bb = {'battery_pct': 10}
        result = planner._action_check_battery({'min_pct': '20'}, bb)
        assert result == BTStatus.FAILURE

    def test_battery_missing_defaults_ok(self, planner):
        """Missing battery_pct defaults to 100 -> SUCCESS."""
        result = planner._action_check_battery({}, {})
        assert result == BTStatus.SUCCESS


# ===== Patrol generation =====

class TestPatrolGeneration:
    """Test _action_generate_patrol creates correct waypoints."""

    def test_generates_correct_count(self, planner):
        planner.current_pose = (0.0, 0.0, 0.0)
        bb = {}
        result = planner._action_generate_patrol({'points': '6', 'radius': '3.0'}, bb)
        assert result == BTStatus.SUCCESS
        assert len(bb['patrol_queue']) == 6

    def test_default_count_and_radius(self, planner):
        planner.current_pose = (0.0, 0.0, 0.0)
        bb = {}
        planner._action_generate_patrol({}, bb)
        # Default: patrol_points=8, patrol_radius=5.0
        assert len(bb['patrol_queue']) == 8

    def test_waypoints_on_circle(self, planner):
        """All generated points should be at the correct radius from centre."""
        planner.current_pose = (0.0, 0.0, 0.0)
        bb = {}
        radius = 5.0
        planner._action_generate_patrol({'radius': str(radius)}, bb)

        for x, y in bb['patrol_queue']:
            dist = math.hypot(x, y)
            assert dist == pytest.approx(radius, abs=1e-6)

    def test_waypoints_equally_spaced(self, planner):
        """Adjacent waypoints should be equally spaced angularly."""
        planner.current_pose = (0.0, 0.0, 0.0)
        bb = {}
        n = 8
        planner._action_generate_patrol({'points': str(n)}, bb)

        angles = [math.atan2(y, x) for x, y in bb['patrol_queue']]
        expected = 2 * math.pi / n
        for i in range(len(angles) - 1):
            diff = angles[i + 1] - angles[i]
            # Normalize to [0, 2*pi) to handle atan2 wrapping at +/-pi
            diff = diff % (2 * math.pi)
            assert diff == pytest.approx(expected, abs=1e-6)

    def test_patrol_centered_on_current_pose(self, planner):
        """Waypoints should be centered on the rover's current position."""
        planner.current_pose = (10.0, 5.0, 0.0)
        bb = {}
        radius = 3.0
        planner._action_generate_patrol({'radius': str(radius)}, bb)

        for x, y in bb['patrol_queue']:
            dist = math.hypot(x - 10.0, y - 5.0)
            assert dist == pytest.approx(radius, abs=1e-6)


# ===== Wait action =====

class TestWaitAction:
    """Test the _action_wait handler."""

    def test_wait_returns_running_initially(self, planner):
        bb = {}
        result = planner._action_wait({'seconds': '10.0'}, bb)
        assert result == BTStatus.RUNNING

    def test_wait_completes_after_duration(self, planner):
        bb = {}
        params = {'seconds': '0.01'}
        planner._action_wait(params, bb)
        time.sleep(0.02)
        result = planner._action_wait(params, bb)
        assert result == BTStatus.SUCCESS

    def test_wait_cleans_up_blackboard(self, planner):
        bb = {}
        params = {'seconds': '0.01'}
        planner._action_wait(params, bb)
        time.sleep(0.02)
        planner._action_wait(params, bb)
        # The start key should be cleaned up after completion
        wait_keys = [k for k in bb if k.startswith('_wait_start_')]
        assert len(wait_keys) == 0


# ===== Log action =====

class TestLogAction:
    def test_log_returns_success(self, planner):
        result = planner._action_log({'message': 'test'}, {})
        assert result == BTStatus.SUCCESS


# ===== Simple patrol BT structure =====

class TestSimplePatrolBT:
    """Test the built-in simple patrol behaviour tree."""

    def test_build_simple_patrol_structure(self, planner):
        bt = planner._build_simple_patrol()
        assert isinstance(bt, SequenceNode)
        assert len(bt.children) == 3
        assert isinstance(bt.children[0], ConditionNode)  # battery check
        assert isinstance(bt.children[1], ActionNode)  # generate patrol
        assert isinstance(bt.children[2], RepeatNode)  # patrol loop

    def test_simple_patrol_fails_on_low_battery(self, planner):
        bt = planner._build_simple_patrol()
        bb = dict(planner.blackboard)
        bb['battery_ok'] = False
        result = bt.tick(bb)
        assert result == BTStatus.FAILURE

    def test_simple_patrol_generates_and_starts(self, planner):
        bt = planner._build_simple_patrol()
        bb = dict(planner.blackboard)
        bb['battery_ok'] = True
        planner.current_pose = (0.0, 0.0, 0.0)

        result = bt.tick(bb)
        # Should succeed on battery check, succeed on generate patrol,
        # then start the patrol loop (RUNNING)
        assert result == BTStatus.RUNNING
        assert 'patrol_queue' in bb
