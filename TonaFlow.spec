# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['TonaFlow.py'],
    pathex=[],
    binaries=[],
    datas=[('imgs/launch_icons/TF.icns', 'imgs/launch_icons'),
 ('imgs/launch_icons/TF.ico', 'imgs/launch_icons'),
 ('imgs/logos/TonaFlow_DarkMode.png', 'imgs/logos'),
 ('imgs/logos/TonaFlow_LightMode.png', 'imgs/logos'),
 ('imgs/icons/plus-2.svg', 'imgs/icons'),
 ('imgs/icons/row-remove.svg', 'imgs/icons'),
 ('imgs/icons/minus.svg', 'imgs/icons'),
 ('imgs/icons/Infobar/light/removeheartbeat.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/samplingpoints.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/addheartbeat.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/showpartialcalc.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/showfiltered.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/removedbeats.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/light/insertremovalregion.svg', 'imgs/icons/Infobar/light'),
 ('imgs/icons/Infobar/dark/removeheartbeat.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/samplingpoints.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/addheartbeat.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/showpartialcalc.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/showfiltered.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/removedbeats.svg', 'imgs/icons/Infobar/dark'),
 ('imgs/icons/Infobar/dark/insertremovalregion.svg', 'imgs/icons/Infobar/dark'),
 ('configs/configs.ini', 'ssqueezepy/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TonaFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon = './imgs/launch_icons/tf.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TonaFlow',
)
app = BUNDLE(
    coll,
    name='TonaFlow.app',
    icon='./imgs/launch_icons/tf.icns',
    bundle_identifier=None,
)
