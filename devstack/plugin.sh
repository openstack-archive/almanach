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

    iniset $ALMANACH_CONF DEFAULT debug "True"

    iniset $ALMANACH_CONF api bind_ip $ALMANACH_SERVICE_HOST
    iniset $ALMANACH_CONF api bind_port $ALMANACH_SERVICE_PORT

    iniset $ALMANACH_CONF auth strategy keystone

    iniset $ALMANACH_CONF keystone_authtoken username almanach
    iniset $ALMANACH_CONF keystone_authtoken password $SERVICE_PASSWORD
    iniset $ALMANACH_CONF keystone_authtoken user_domain_id default
    iniset $ALMANACH_CONF keystone_authtoken user_domain_name $SERVICE_DOMAIN_NAME
    iniset $ALMANACH_CONF keystone_authtoken project_domain_name $SERVICE_DOMAIN_NAME
    iniset $ALMANACH_CONF keystone_authtoken project_name $SERVICE_PROJECT_NAME
    iniset $ALMANACH_CONF keystone_authtoken auth_url $KEYSTONE_SERVICE_URI_V3

    iniset $ALMANACH_CONF collector transport_url rabbit://$RABBIT_USERID:$RABBIT_PASSWORD@$RABBIT_HOST:5672

    iniset $ALMANACH_CONF database connection_url mongodb://localhost/almanach

    iniset $ALMANACH_CONF entities instance_image_meta distro,version,os_type
}

function almanach_configure_external_services {
    if is_service_enabled nova; then
        iniset $NOVA_CONF DEFAULT notification_topics "almanach,notifications"
    fi

    if is_service_enabled cinder; then
        iniset $CINDER_CONF oslo_messaging_notifications topics "almanach,notifications"
        iniset $CINDER_CONF oslo_messaging_notifications driver "messagingv2"
    fi
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
    run_process almanach-collector "$ALMANACH_BIN_DIR/almanach-collector --config-file $ALMANACH_CONF"
    run_process almanach-api "$ALMANACH_BIN_DIR/almanach-api --config-file $ALMANACH_CONF"
}

function stop_almanach {
    for serv in almanach-api almanach-collector; do
        stop_process $serv
    done
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
        almanach_configure_external_services
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
