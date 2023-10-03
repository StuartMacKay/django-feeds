def data_is_empty(form) -> bool:
    return form.data == {}


def cleaned_data_is_empty(form) -> bool:
    return form.cleaned_data == {}


def form_is_bound(response, key="form") -> bool:
    form = response.context.get(key)
    return form.is_bound


def form_is_valid(response, key="form") -> bool:
    form = response.context.get(key)
    return form.is_valid()


def form_is_reset(response, key="form") -> bool:
    form = response.context.get(key)
    return form and data_is_empty(form) and cleaned_data_is_empty(form)
