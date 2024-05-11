import os
# Install as a service


def install_service():
    print("Installing service")
    if os.name == "nt":
        print("Windows service installation not yet implemented")
    else:
        print("Installing as a systemd service")
        with open("/etc/systemd/system/authentik-wallpaper.service", "w") as f:
            f.write(
                f"""[Unit]
Description=Authentik Wallpaper Service
After=network.target
                
[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.path.join(os.getcwd(), "service.py")}
Restart=on-failure
                
[Install]
WantedBy=multi-user.target"""
            )