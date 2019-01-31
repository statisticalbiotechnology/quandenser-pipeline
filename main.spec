# -*- mode: python -*-

block_cipher = None


datas = [("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/plugins", 'PySide2/Qt/plugins'),
         ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/libexec", 'PySide2/Qt/libexec'),
         ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/translations", 'PySide2/Qt/translations')]

a = Analysis(['main.py'],
             pathex=['/media/storage/timothy/quandenser-pipeline'],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
