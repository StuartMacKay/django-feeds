from django.forms import model_to_dict


def get_fields(obj):
    return model_to_dict(obj, fields=[field.name for field in obj._meta.fields])  # noqa


def get_updated(obj):
    return obj._meta.model.objects.get(pk=obj.id)  # noqa


def changed_fields(obj, *names) -> bool:
    d1 = get_fields(obj)
    d2 = get_fields(get_updated(obj))
    changed = [k for k, v in d1.items() if v != d2[k]]
    return sorted(names) == sorted(changed)
