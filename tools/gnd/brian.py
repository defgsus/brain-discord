

def get_discord_result(query):
    from .api import make_query
    results = make_query(query)

    if not results:
        return "Nix"

    ret = ""
    for r in results:
        if "preferredNameForTheConferenceOrEvent" in r:
            rtype = "Event"
            text = "%(preferredNameForTheConferenceOrEvent)s" % r
            if r.get("dateOfConferenceOrEvent"):
                text += ", %(dateOfConferenceOrEvent)s" % r
            text += "\n"

        elif "preferredNameForTheWork" in r:
            rtype = "Work"
            text = "%(preferredNameForTheWork)s" % r
            if r.get("dateOfPublication"):
                text += ", %(dateOfPublication)s" % r
            text += "\n"
            vari = to_multi_line(r.get("variantNameForTheWork"), " / ")
            if vari:
                text += "%s\n" % vari
            info = to_multi_line(r.get("biographicalOrHistoricalInformation"))
            if info:
                text += info + "\n"
            info = to_multi_line(r.get("definition"))
            if info:
                text += info

        elif "preferredNameForTheCorporateBody" in r:
            rtype = "Firma"
            text = "%(preferredNameForTheCorporateBody)s" % r
            if "dateOfEstablishment" in r:
                text += ", %(dateOfEstablishment)s" % r
            text += "\n"
            defi = to_multi_line(r.get("definition"))
            if defi:
                text += defi

        elif "preferredNameForTheSubjectHeading" in r:
            rtype = "Ding"
            text = "%(preferredNameForTheSubjectHeading)s\n" % r

        elif "preferredNameForThePerson" in r:
            rtype = "Person"
            text = "%(preferredNameForThePerson)s" % r
            if r.get("dateOfBirth"):
                text += ", %(dateOfBirth)s" % r
                if r.get("dateOfDeath"):
                    text += " - %(dateOfDeath)s" % r
            text += "\n"
            info = to_multi_line(r.get("biographicalOrHistoricalInformation"))
            if info:
                text += info

        else:
            rtype = "Unbekannt"
            text = repr(r)

        ret += "**%s**: " % rtype
        ret += "http://d-nb.info/gnd/%(gndIdentifier)s\n" % r
        ret += "```\n%s```\n" % text

    return ret


def to_multi_line(value, sep="\n"):
    if not value:
        return None

    if not isinstance(value, list):
        value = [value]

    return sep.join(value)
