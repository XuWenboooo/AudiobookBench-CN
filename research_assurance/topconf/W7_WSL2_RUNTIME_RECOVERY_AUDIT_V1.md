# W7 WSL2 runtime recovery audit v1

System-level authorization was used to enable `Microsoft-Windows-Subsystem-Linux` and `VirtualMachinePlatform` through elevated DISM. Both features completed with exit code 3010, a reboot was performed, and the features are now enabled.

The official WSL bootstrap and `wsl --update --web-download` paths returned a repeated remote 403 failure. The official Microsoft WSL 2.7.14 x64 MSI was identified with its expected size and SHA256, but the GitHub transfer timed out and no installer bytes were accepted. Ubuntu-22.04, the WSL runtime/kernel, and all three isolated research runtimes therefore remain absent.

No Linux NVIDIA driver was installed, the Windows Python environment was not modified, and no model asset or partial archive was promoted. V4, V6, and final PASS readiness remain gated. No W7 case, Level-2 outcome, metric, or scientific inference was run.
