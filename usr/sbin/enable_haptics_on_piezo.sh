#! /bin/sh

# Disabled, this is obsoleted but still needed due to NB#154615
echo "Obsoleted, do not use"
exit 0

if [[ "$1" == "--enable-on-rd-image-only" ]]; then
    (osso-product-info -q OSSO_VERSION|grep -q RD) || exit 0
fi

echo Enabling haptic feedback on piezo element
    
# For the Speaker:
amixer -q -Dhw:n950twl4030 sset 'PredriveR Mixer AudioL2' on # PreDriveR audio is coming from the DACL2 (TDM channel 1)
amixer -q -Dhw:n950twl4030 sset 'PreDriv' 0,2                # Set the PreDrive right output gain to 0 dB
amixer -q -Dhw:n950twl4030 sset 'Speaker Function' On        # Enable the external amplifier for the speakers

#For piezo:
amixer -q -Dhw:n950twl4030 sset 'HeadsetL Mixer AudioL2' on  # HeadsetL audio is routed from DACL2 (I2S left)
amixer -q -Dhw:n950twl4030 sset 'Headset' 2,0                # Set the HeadsetL volume only

#Adjust volumes
amixer -q sset 'DAC2 Digital Coarse' 2,1
amixer -q sset 'DAC2 Digital Fine' 53,50
amixer -q sset 'DAC2 Analog' 14,13
