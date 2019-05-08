set VBoxManage="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
%VBoxManage% || (curl https://download.virtualbox.org/virtualbox/6.0.6/VirtualBox-6.0.6-130049-Win.exe --output virtualbox.exe) & virtualbox.exe
%VBoxManage% list vms | findstr QP_windows
if %ERRORLEVEL% == 1 (
  curl -L "https://onedrive.live.com/download?cid=608C90DCC6593D31&resid=608C90DCC6593D31%%2192447&authkey=AGIQYfu6_AL7I8M" --output QP_windows.ova
  %VBoxManage% import QP_windows.ova
)
%VBoxManage% sharedfolder remove QP_windows --name share
%VBoxManage% sharedfolder add QP_windows --name share --hostpath "C:\\" --automount
%VBoxManage% startvm QP_windows
