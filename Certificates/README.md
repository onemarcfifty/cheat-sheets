# X.509 Certificates

You can create X.509 certificates on the command line with openssl or in a GUI, for example with [XCA by Christian Hohnstaedt](https://hohnstaedt.de/xca)

Check the certificate videos on my YouTube channel for details.

In the `ansible-playbooks` subdirectory you can find some playbooks that I use for distribution of LetsEncrypt certificates in my LAN.

## Create a CA

### Generate the CA root key

    # add -aes256 in order to encrypt the key with a password
    openssl genrsa -aes256 -out "ca-root.key" 4096

### Create CA certificate

    # this will ask for all necessary details - you could add
    # the parameters into a .cnf file or
    # specify them on the command line
    # the validity is 10 years (3650 days)
    openssl req -x509 -new -nodes -key ca-root.key -sha256 -days 3650 -out ca-root.crt

## Create a Server Certificate

### Generate a private key for a Server

    openssl genrsa -out "server.key" 4096

### Generate and sign the Certificate Signing Request (CSR)

    openssl req -new -key "server.key" -out "server.csr" -sha256 -subj '/CN=myserver.mydomain.com'

### Sign the Server CSR with the CA key

    # Typically you would have a config file and specify more
    # parameters inside that file (alt_names etc.)
    # add the cnf file with the -extfile parameter
    openssl x509 -req -in server.csr -CA ca-root.crt -CAkey ca-root.key -CAcreateserial -out server.crt -days 365
