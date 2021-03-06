set VBoxManage="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
%VBoxManage% || (
curl https://download.virtualbox.org/virtualbox/6.0.6/VirtualBox-6.0.6-130049-Win.exe --output virtualbox.exe
virtualbox.exe)
%VBoxManage% list vms | findstr QP_windows
if %ERRORLEVEL% == 1 (
  curl -L "https://onedrive.live.com/download?cid=608C90DCC6593D31&resid=608C90DCC6593D31%%2193233&authkey=AABHkrO62lXMjI8" --output QP_windows.ova
  %VBoxManage% import QP_windows.ova
)
%VBoxManage% sharedfolder remove QP_windows --name share
%VBoxManage% sharedfolder add QP_windows --name share --hostpath "C:\\" --automount
%VBoxManage% setextradata QP_windows VBoxInternal2/SharedFoldersEnableSymlinksCreate/share 1
%VBoxManage% startvm QP_windows
