<h1 align="center">Fedora Development Environment Profiler</h1>

<div align="center">
  <strong>A read-only, native Fedora Workstation desktop application that profiles installed development toolchains, background services, and resource usage.</strong>
</div>
<br>

<div align="center">
  <img src="https://img.shields.io/badge/Fedora-31A8FF?style=for-the-badge&logo=fedora&logoColor=white" alt="Fedora">
  <img src="https://img.shields.io/badge/GTK4-7FE719?style=for-the-badge&logo=gtk&logoColor=white" alt="GTK4">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</div>

---

## 🌟 Overview

The **Fedora Development Environment Profiler** is a secure, observability-focused tool built natively for Fedora Workstation (GNOME/Wayland). It allows developers to quickly inspect what development toolchains (e.g., Python, Node.js, Rust, Docker) are installed on their machines, what systemd services or user daemons they rely on, and whether they are actively running or simply taking up space.

**Crucially, this application is completely read-only.** It makes zero modifications to your system, deletes no files, and stops no services. It exists purely to bring visibility to your environment stack footprint using safe, native APIs.

## ✨ Features

- **Safe & Read-Only:** Strictly observational. Never modifies, removes, or stops any part of your system. There are no actionable buttons.
- **Beginner-Friendly & Neutral:** Explicitly designed to reassure rather than alarm. Drops technical jargon and optimization scores in favor of plain-language explanations.
- **Desktop Environment Agnostic:** Dynamically detects GNOME, KDE Plasma, Hyprland, XFCE, Cinnamon, MATE, or minimal Wayland/X11 sessions. It separates core OS daemons from your specific desktop's background services without assumptions.
- **Stack Detection:** Automatically groups raw RPM packages and system processes into understandable "Stacks" (Python, Node.js, Java, Go, Rust, and Containerization via Docker/Podman).
- **Service & Daemon Correlation:** Maps running background processes and `systemd` (both system and user session) units back to their parent toolchain.
- **Neutral Activity Heuristics:** Observes stack activity (Active or Idle) by checking recent file accesses and currently running daemons, without suggesting cleanups.
- **Native UI:** Built with GTK 4 and `libadwaita` for a seamless, modern, responsive experience conforming to the GNOME Human Interface Guidelines (HIG) but fully usable anywhere.

- **Export & Diagnostics:** Built-in JSON export feature providing a safe, read-only diagnostic snapshot of the system state for bug reports.
- **Strict Error Handling:** Never fails silently. Partial data limits due to permissions or DBus restrictions are gracefully surfaced to the user without blocking the UI.
- **Transparent Methodology:** Features an accessible "How Detection Works" dialog directly in the app menu openly discussing the heuristics used for classifications.

## 🏗️ Architecture (How it Works)
- **Frontend**: `Adw.ApplicationWindow` built on GTK 4, tested to be responsive on standard DEs and Wayland Tiling Window Managers alike.
- **Backend Data**: Combines `rpm -qa`, `org.freedesktop.systemd1` via D-Bus, and `psutil` process mapping.
- **Caching**: Employs deterministic per-session data caching to guarantee analysis stability while navigating.

1. **System Inspection Layer**
   - **`systemd_client.py`**: Securely queries the DBus API (`org.freedesktop.systemd1`) via `Gio.DBusProxy` to fetch active services, sockets, and timers.
   - **`package_mgr.py`**: Interrogates the local RPM database natively to map tools to installed packages, avoiding network calls or cache updates.
   - **`process_monitor.py`**: Wraps `psutil` to safely inspect active process trees.
   - **`stack_detector.py`**: Checks `$PATH` and known installation directories to flag available toolchains.

2. **Analysis Layer**
   - **`correlator.py`**: Takes raw DBus services, RPMs, and process data, grouping them dynamically into recognized stacks based on naming conventions and binary paths.
   - **`heuristics.py`**: Evaluates the access timestamps (`st_atime`) of primary binaries and cross-references active DBus units to determine if a stack is actively used or idle. Provides human-readable explanations.

3. **UI Layer**
   - Engineered exclusively with `Gtk 4.0` and `Adw 1`.
   - Uses `Adw.NavigationView` for smooth sliding transitions between the global **Overview Summary** and specific **Stack Detail Pages**.
   - Loads system data asynchronously over `GLib.idle_add` to ensure the Wayland window never hangs during metadata fetching.

## 🚀 Getting Started

### Prerequisites

Ensure you are running a recent version of Fedora Workstation with the following dependencies:

```bash
sudo dnf install python3-gobject python3-psutil gtk4 libadwaita
```

### Running from Source

You do not need to install the package system-wide to test it out. Simply clone the repository and run the Python module natively:

```bash
git clone https://github.com/yourusername/fedora-dev-profiler.git
cd fedora-dev-profiler
python3 -m fedora_dev_profiler
```

### Building and Installing the RPM

Since this application is tailored specifically for Fedora, we recommend packaging and installing it natively as an RPM. The project includes a `fedora-dev-profiler.spec` file ready for `rpmbuild`.

```bash
# Install required RPM macros
sudo dnf install rpm-build pyproject-rpm-macros python3-devel

# Setup build directory
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Archive the source and copy it
tar -czvf ~/rpmbuild/SOURCES/fedora-dev-profiler-0.1.0.tar.gz .
cp fedora-dev-profiler.spec ~/rpmbuild/SPECS/

# Build the RPM
rpmbuild -ba ~/rpmbuild/SPECS/fedora-dev-profiler.spec

# Install the resulting RPM
sudo rpm -i ~/rpmbuild/RPMS/noarch/fedora-dev-profiler-0.1.0-1.*.rpm
```

Once installed, simply search for **Fedora Dev Profiler** in your GNOME Activities overview.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. If you are adding a new Development Stack heuristic, ensure that:
1. It queries purely read-only commands/DBus calls.
2. It handles exceptions gracefully (e.g., if a user lacks permissions to view a specific root DBus property).
3. The UI components use standard `Adw.ActionRow` and `Adw.PreferencesGroup` properties without hacky CSS overrides to maintain GNOME consistency.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
