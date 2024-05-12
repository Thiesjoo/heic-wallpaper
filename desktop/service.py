import os
import sys


# Install as a service


def install_service():
    print("Service installing is still manual")
    print("Below are the examples for different platforms")
    print("Removing manual services is also manual, usually by removing the new service")

    if sys.platform == "win32":
        print("To add this as a service, you can use the Windows Scheduler. Run this executable every 5 minutes.")
    elif sys.platform == "darwin":
        print("To add this as a service, you can use launchd")
        print("Example: ")
        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        print("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">")
        print("<plist version=\"1.0\">")
        print("<dict>")
        print("    <key>Label</key>")
        print("    <string>com.example.runme</string>")
        print("    <key>ProgramArguments</key>")
        print("    <array>")
        print("        <string>/path/to/executable</string>")
        print("    </array>")
        print("    <key>StartInterval</key>")
        print("    <integer>300</integer>")
        print("</dict>")
        print("</plist>")
    else:
        print("To add this as a service, you can use crontab")
        print("Example: ")
        print("*/5 * * * * /path/to/executable")