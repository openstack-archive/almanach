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

    sleep 5
}

function almanach_configure {
    sudo install -d -o $STACK_USER -m 755 $ALMANACH_CONF_DIR
    cp ${ALMANACH_DIR}/almanach/resources/config/almanach.cfg $ALMANACH_CONF

    iniset $ALMANACH_CONF ALMANACH auth_token secret
    iniset $ALMANACH_CONF ALMANACH auth_strategy private_key
    iniset $ALMANACH_CONF ALMANACH volume_existence_threshold 60
    iniset $ALMANACH_CONF ALMANACH device_metadata_whitelist metering.billing_mode

    iniset $ALMANACH_CONF MONGODB url mongodb://localhost/almanach
    iniset $ALMANACH_CONF MONGODB database almanach
    iniset $ALMANACH_CONF MONGODB indexes project_id,start,end

    iniset $ALMANACH_CONF RABBITMQ url amqp://stackrabbit:secret@localhost:5672
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
}

function start_almanach {
    run_process almanach-collector "$ALMANACH_BIN_DIR/almanach collector $ALMANACH_CONF"
    run_process almanach-api "$ALMANACH_BIN_DIR/almanach api $ALMANACH_CONF --host 0.0.0.0"
}

function stop_almanach {
    echo "todo"
}

ALMANACH_BIN_DIR=$(get_python_exec_prefix)

if is_service_enabled almanach-api almanach-collector; then
    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        echo_summary "Installing MongoDB"
        _install_mongodb
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Almanach"
        install_almanach
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Almanach"
        almanach_configure
        almanach_create_accounts
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Almanach"
        start_almanach
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_almanach
    fi

    if [[ "$1" == "clean" ]]; then
        _almanach_drop_database
    fi
fi
