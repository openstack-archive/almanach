#The current full list of mode and phase are:
#
# stack - Called by stack.sh four times for different phases of its run:
#
#   pre-install - Called after system (OS) setup is complete and before project source is installed.
#
#   install - Called after the layer 1 and 2 projects source and their dependencies have been installed.
#
#   post-config - Called after the layer 1 and 2 services have been configured.
#                  All configuration files for enabled services should exist at this point.
#
#   extra - Called near the end after layer 1 and 2 services have been started.
#
#   test-config - Called at the end of devstack used to configure tempest or any other test environments
#
# unstack - Called by unstack.sh before other services are shut down.
#
# clean - Called by clean.sh before other services are cleaned, but after unstack.sh has been called.

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set -o xtrace

function almanach_service_url {
    echo "$ALMANACH_SERVICE_PROTOCOL://$ALMANACH_SERVICE_HOST:$ALMANACH_SERVICE_PORT"
}

function _install_mongodb {
    # Server package is the same on all
    local packages=mongodb-server

    if is_fedora; then
        # mongodb client
        packages="${packages} mongodb"
    fi

    install_package ${packages}

    if is_fedora; then
        restart_service mongod
    else
        restart_service mongodb
    fi

    # give time for service to restart
    sleep 5
}

function almanach_configure {
    iniset $ALMANACH_CONF ALMANACH auth_token secret
    iniset $ALMANACH_CONF ALMANACH auth_strategy private_key
    iniset $ALMANACH_CONF ALMANACH volume_existence_threshold 60
    iniset $ALMANACH_CONF ALMANACH device_metadata_whitelist metering.billing_mode

    iniset $ALMANACH_CONF MONGODB url mongodb://almanach:almanach@localhost:27017/almanach
    iniset $ALMANACH_CONF MONGODB database almanach
    iniset $ALMANACH_CONF MONGODB indexes project_id,start,end

    iniset $ALMANACH_CONF RABBITMQ url amqp://openstack:openstack@localhost:5672
    iniset $ALMANACH_CONF RABBITMQ indexes project_id,start,end
    iniset $ALMANACH_CONF RABBITMQ queue almanach.info
    iniset $ALMANACH_CONF RABBITMQ exchange almanach.info
    iniset $ALMANACH_CONF RABBITMQ routing.key almanach.info
    iniset $ALMANACH_CONF RABBITMQ retry.time.to.live 10
    iniset $ALMANACH_CONF RABBITMQ retry.exchange almanach.retry
    iniset $ALMANACH_CONF RABBITMQ retry.maximum 3
    iniset $ALMANACH_CONF RABBITMQ retry.queue almanach.retry
    iniset $ALMANACH_CONF RABBITMQ retry.return.exchange almanach
    iniset $ALMANACH_CONF RABBITMQ dead.queue almanach.dead
    iniset $ALMANACH_CONF RABBITMQ dead.exchange almanach.dead
}

# Create almanach related accounts in Keystone
function almanach_create_accounts {
    OLD_OS_CLOUD=$OS_CLOUD
    export OS_CLOUD='devstack-admin'

    create_service_user "almanach" "admin"

    get_or_create_service "almanach" "usage" "Almanach Resource Utilization Service"
    get_or_create_endpoint "usage" \
        "$REGION_NAME" \
        "$(almanach_service_url)" \
        "$(almanach_service_url)" \
        "$(almanach_service_url)"

    export OS_CLOUD=$OLD_OS_CLOUD
}

function _almanach_drop_database {
    mongo almanach --eval "db.dropDatabase();"
}

function install_almanach {
    setup_develop $ALMANACH_DIR

    sudo install -d -o $STACK_USER -m 755 $ALMANACH_CONF_DIR
}

function start_almanach {
    run_process almanach-collector "$ALMANACH_BIN_DIR/almanach collector $ALMANACH_CONF"
    run_process almanach-api "$ALMANACH_BIN_DIR/almanach api $ALMANACH_CONF --host 0.0.0.0"
}

ALMANACH_BIN_DIR=$(get_python_exec_prefix)

if is_service_enabled almanach; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services Template"
        _install_mongodb

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Template"
        install_almanach

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Almanach"
        almanach_configure
        almanach_create_accounts

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the template service
        echo_summary "Initializing Almanach"
        start_almanach
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down template services
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        _almanach_drop_database
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi