login_json_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"}
    },
}

register_json_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
        "re_password": {"type": "string"}
    },
}

submit_charging_request_json_schema = {
    "type": "object",
    "properties": {
        "charge_mode": {"type": "string"},
        "require_amount": {"type": "number"},
        "battery_size": {"type": "number"}
    },
}

edit_charging_request_json_schema = {
    "type": "object",
    "properties": {
        "charge_mode": {"type": "string"},
        "require_amount": {"type": "number"}
    },
}

update_pile_json_schema = {
    "type": "object",
    "properties": {
        "charger_id": {"type": "string"},
        "status": {"type": "string"},
    }
}