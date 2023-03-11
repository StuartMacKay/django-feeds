from django.contrib import messages


def redirects_to(response, url) -> bool:
    if hasattr(response, "redirect_chain"):
        redirect_url, status_code = response.redirect_chain[-1]
    else:
        status_code = response.status_code
        redirect_url = response.url
    return status_code == 302 and redirect_url == url


def is_error_message(message) -> bool:
    return message.level == messages.ERROR


def is_warning_message(message) -> bool:
    return message.level == messages.WARNING


def is_success_message(message) -> bool:
    return message.level == messages.SUCCESS


def success_message_shown(response) -> bool:
    objs = list(response.context.get("messages", []))
    return bool(objs and len(objs) == 1) and is_success_message(objs[0])


def warning_message_shown(response) -> bool:
    objs = list(response.context.get("messages", []))
    return bool(objs and len(objs) == 1) and is_warning_message(objs[0])


def error_message_shown(response) -> bool:
    objs = list(response.context.get("messages", []))
    return bool(objs and len(objs) == 1) and is_error_message(objs[0])
