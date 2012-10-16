#!/bin/sh

set_sysfs_value()
{
    name=$1
    location=$2

    if [ "$(cat ${location})" != "${name}" ]
    then
        echo -n ${name} > ${location} \
            || echo "ERROR: pulseaudio_pre-start.sh: Failed to set ${location} to ${name}" > /dev/console
    fi
}

# The following settings should be used for McBSP ports:
# /sys/devices/platform/omap-mcbsp.2/dma_op_mode -> threshold (extended)
# /sys/devices/platform/omap-mcbsp.3/dma_op_mode -> threshold (extended)
# /sys/devices/platform/omap-mcbsp.4/dma_op_mode -> threshold (extended)

# Element mode is enabled by default. Enable threshold mode on all McBSP ports.
set_sysfs_value "threshold" /sys/devices/platform/omap-mcbsp.2/dma_op_mode
set_sysfs_value "threshold" /sys/devices/platform/omap-mcbsp.3/dma_op_mode
set_sysfs_value "threshold" /sys/devices/platform/omap-mcbsp.4/dma_op_mode


# Enable the use of almost the whole FIFO on all McBSP ports. Using the
# absolute maximum buffer size can cause problems: the DMA transfer apparently
# isn't fast enough, and the symptom is crackling sound. These values should be
# selected so that the buffers are as big as possible without crackling.

# McBSP2 has 1280 (1024 + 256) word long buffer on both tx and rx (rx isn't
# used). 1280 - 1200 = 80 bytes of safety margin.
set_sysfs_value 1200 /sys/devices/platform/omap-mcbsp.2/max_tx_thres

# McBSP3, 4 (and 1, 5) have 128 word long FIFO for tx and rx. 128 - 120 = 8
# bytes of safety margin.
set_sysfs_value 120 /sys/devices/platform/omap-mcbsp.3/max_tx_thres
set_sysfs_value 120 /sys/devices/platform/omap-mcbsp.3/max_rx_thres
set_sysfs_value 120 /sys/devices/platform/omap-mcbsp.4/max_tx_thres
set_sysfs_value 120 /sys/devices/platform/omap-mcbsp.4/max_rx_thres


# FIXME: This is a temporary thing, see NB#188212.
set_sysfs_value n950twl4030 /sys/class/sound/card0/id
set_sysfs_value n950tlv320dac33 /sys/class/sound/card1/id
set_sysfs_value n950wl1273 /sys/class/sound/card2/id

# Set initial values to 100% for controlling volumes.
# This becomes obsolete when device-restore is extended to support
# initialization of 100% sink volumes, regardless of the original mixer values.
amixer -Dhw:n950twl4030 sset "DAC2 Analog" 12 \
 || echo "ERROR: pulseaudio_pre-start.sh: Failed to set DAC2 Analog" > /dev/console
amixer -Dhw:n950tlv320dac33 sset "TPA6140A2 Headphone" 21 \
 || echo "ERROR: pulseaudio_pre-start.sh: Failed to set TPA6140A2 Headphone" > /dev/console

/sbin/modprobe cmt_speech
/bin/chown root:pulse /dev/cmt_speech
