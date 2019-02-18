# -*- mode: python -*-

block_cipher = None


datas = [("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/plugins", 'PySide2/Qt/plugins'),
         ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/libexec", 'PySide2/Qt/libexec'),
         ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/translations", 'PySide2/Qt/translations'),
         ("config", 'config'),
         ("fonts", 'fonts'),
         ("images", 'images'),
         ("tab1", 'tab1'),
         ("tab2", 'tab2'),
         ("tab3", 'tab3"'),
         ("tab4", 'tab4'),
         ("tab5", 'tab5'),
         ("tooltip_label.py", 'tooltip_label.py'),
         ("utils.py", 'utils.py'),
         ("custom_config_parser.py", 'custom_config_parser.py'),
         ("__init__.py", '__init__.py')]

a = Analysis(['main.py'],
             pathex=['/media/storage/timothy/quandenser-pipeline/dependencies/ui'],
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
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
