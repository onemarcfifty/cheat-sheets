## VM stuff (KVM/QEMU)


## VM creation and disk import

(from the proxmox-autodeploy repo)

    qm create $OPENWRTID --cores 1 --name "OpenWrt" --net0 model=virtio,bridge=$OPENWRT_IF --net1 model=virtio,bridge=$EGRESS_IF --storage $DEFAULT_STORAGE --memory 512
    # download OpenWrt image and unzip on the fly
    wget -O - $OPENWRTURL | gunzip -c >/tmp/openwrt.img
    # import into the OpenWrt VM and attach it
    qm importdisk $OPENWRTID /tmp/openwrt.img $DEFAULT_STORAGE --format qcow2
    qm set $OPENWRTID --ide0 $DEFAULT_STORAGE:vm-$OPENWRTID-disk-0
    qm set $OPENWRTID --boot order=ide0
    # now remove the temporary image
    rm /tmp/openwrt.img
