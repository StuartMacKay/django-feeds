from django.core import mail


def matches(obj, **kwargs):
    results = []
    for k, v in kwargs.items():
        if hasattr(obj, k) and getattr(obj, k):
            results.append(True)
        else:
            results.append(False)
    return all(results)


def emails_equal(e1, e2) -> bool:
    return (
        e1.to == e2.to and e1.from_email == e2.from_email and e1.subject == e2.subject
    )


def email_was_sent(sender, receiver) -> bool:
    def _matches(item):
        return matches(item, to=[receiver], from_email=sender)

    return any(map(_matches, mail.outbox))


def email_not_sent() -> bool:
    return len(mail.outbox) == 0
