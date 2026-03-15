#!/bin/bash
# =============================================================================
# Mars Rover ROS2 Workspace Setup Script
# =============================================================================
# Sets up the colcon workspace, symlinks packages, installs dependencies,
# and builds everything.
#
# Usage:
#   chmod +x rover_ws_setup.sh
#   ./rover_ws_setup.sh
#
# Requirements:
#   - ROS2 Humble (or later) installed and sourced
#   - colcon build tools installed
#   - rosdep initialized
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="${HOME}/rover_ws"
PACKAGES=(
    "rover_msgs"
    "rover_hardware"
    "rover_bringup"
    "rover_perception"
    "rover_navigation"
    "rover_autonomy"
    "rover_teleop"
)

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check ROS2 is sourced
if [ -z "${ROS_DISTRO:-}" ]; then
    log_error "ROS2 is not sourced. Run: source /opt/ros/<distro>/setup.bash"
    exit 1
fi
log_info "Using ROS2 ${ROS_DISTRO}"

# Create workspace
log_info "Creating workspace at ${WS_DIR}"
mkdir -p "${WS_DIR}/src"

# Symlink packages from this directory into the workspace
log_info "Symlinking packages..."
for pkg in "${PACKAGES[@]}"; do
    src_path="${SCRIPT_DIR}/${pkg}"
    link_path="${WS_DIR}/src/${pkg}"

    if [ ! -d "${src_path}" ]; then
        log_warn "Package directory not found: ${src_path}"
        continue
    fi

    if [ -L "${link_path}" ]; then
        rm "${link_path}"
    elif [ -d "${link_path}" ]; then
        log_warn "${link_path} exists and is not a symlink, skipping"
        continue
    fi

    ln -s "${src_path}" "${link_path}"
    log_ok "Linked ${pkg}"
done

# Install dependencies via rosdep
log_info "Installing dependencies with rosdep..."
cd "${WS_DIR}"

if ! command -v rosdep &> /dev/null; then
    log_warn "rosdep not found, skipping dependency installation"
else
    rosdep update --rosdistro="${ROS_DISTRO}" 2>/dev/null || true
    rosdep install --from-paths src --ignore-src -r -y 2>/dev/null || {
        log_warn "Some rosdep dependencies could not be resolved (expected for custom msgs)"
    }
fi

# Install Python dependencies
log_info "Installing Python dependencies..."
pip3 install --user websockets 2>/dev/null || log_warn "Failed to install websockets"

# Build the workspace
log_info "Building workspace with colcon..."
cd "${WS_DIR}"
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | \
    tail -20

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_ok "Build successful!"
else
    log_error "Build failed. Check the output above for errors."
    exit 1
fi

# Source the workspace
log_info "Sourcing workspace..."
source "${WS_DIR}/install/setup.bash"
log_ok "Workspace ready!"

echo ""
echo "============================================="
echo " Mars Rover ROS2 Workspace Setup Complete"
echo "============================================="
echo ""
echo "To use in a new terminal:"
echo "  source /opt/ros/${ROS_DISTRO}/setup.bash"
echo "  source ${WS_DIR}/install/setup.bash"
echo ""
echo "Quick start:"
echo "  # Teleop only (hardware + web control):"
echo "  ros2 launch rover_bringup teleop.launch.py"
echo ""
echo "  # Full system:"
echo "  ros2 launch rover_bringup rover.launch.py"
echo ""
echo "  # Individual nodes:"
echo "  ros2 run rover_navigation ackermann_controller"
echo "  ros2 run rover_teleop web_server_node"
echo ""
