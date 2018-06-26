"""
Originally by
https://www.smallsurething.com/implementing-the-famous-eliza-chatbot-in-python/

translated by bergi

"""
import re
import random


reflections = {
    "bin": "bist",
    "war": "warst",
    "ich": "du",
    "mir": "dir",
    "meine": "deine",
    "mein": "dein",
    "mich": "dich",
    "ich würde": "du würdest",
    "ich hab": "du hast",
    "ich habe": "du hast",
    "ich werde": "du wirst",
    "bist": "bin",
    "du hast": "ich habe",
    "du wirst": "ich werde",
    "dein": "mein",
    "deine": "meine",
    "dich": "mich",
    "du": "ich",
    "dir": "mir",

    "habe": "hast",
    "sehe": "siehst",
    "sage": "sagst",

    "kann": "kannst",
}

psychobabble = [
    [r'Ich brauche (.*)',
     ["Warum brauchst du {0}?",
      "Würde es dir wirklich helfen, {0} zu bekommen?",
      "Bist du sicher, du brauchst {0}?"]],

    [r'Warum machst du nicht ([^\?]*)\??',
     ["Denkst du wirklich ich mache nicht {0}?",
      "Vielleicht mache ich irgendwann {0}.",
      "Willst du wirklich, daß ich {0} mache?"]],

    [r'Warum kann ich nicht ([^\?]*)\??',
     ["Denkst du, du solltest {0}?",
      "Würdest du {0}, was würdest du tun?",
      "Ich weiß nicht -- warum kannst du nicht {0}?",
      "Hast du es wirklich probiert?"]],

    [r'Ich kann nicht (.*)',
     ["Woher weißt du, daß du nicht {0} kannst?",
      "Vielleicht könntest du {0} wenn du probierst.",
      "Was braucht es, damit du {0} kannst?"]],

    [r'Ich bin (.*)',
     ["Bist du zu mir gekommen, weil du {0} bist?",
      "Wie lange bist du schon {0}?",
      "Was denkst du darüber, dass du {0} bist?",
      "Was fühlst du, wenn du {0} bist?",
      "Macht es dir Spaß, {0} zu sein?",
      "Warum sagts du mir, daß du {0} bist?",
      "Warum denkst du, daß du {0} bist?"]],

    [r'Bist du ([^\?]*)\??',
     ["Warum ist es wichtig, daß ich {0} bin?",
      "Wäre es dir lieber, ich wäre nicht {0}?",
      "Vielleicht glaubst du nur, daß ich {0} bin.",
      "Ich bin vielleicht {0} -- was denkst du?"]],

    [r'Was (.*)',
     ["Warum fragst du?",
      "Wie würde dir die Antwort helfen?",
      "Was denkst du?"]],

    [r'Wie (.*)',
     ["Was denkst du denn?",
      "Vielleicht kannst du deine Frage selbst beantworten.",
      "Was willst du wirklich wissen?"]],

    [r'Weil (.*)',
     ["Ist das der wirkliche Grund?",
      "Was gibt es noch für Gründe?",
      "Begründet das auch noch andere Dinge?",
      "Wenn {0}, was stimmt noch?"]],

    [r'(.*) entschuldige (.*)',
     ["Oft ist keine Entschuldigung nötig.",
      "Welche Gefühle hast du, wenn du dich entschuldigst?"]],

    [r'Hallo(.*)',
     ["Hallo... Ich bin froh, dass du heute vorbeigekommen bist.",
      "Tachchen, wie gehts denn heute so?",
      "Hi, wie fühlst du dich heute?"]],

    [r'Ich denke (.*)',
     ["Bezweifelst du {0}?",
      "Denkst du wirklich so?",
      "Aber du bist nicht sicher {0}?"]],

    [r'(.*) Freund(.*)',
     ["Erzähl mir mehr über deine Freunde.",
      "Woran denkst du, wenn du an deine Freunde denkst?",
      "Erzähl mir doch von einem Jugendfreund?"]],

    [r'Ja',
     ["Du scheinst dir sehr sicher zu sein.",
      "OK, aber kannst du das näher erleutern?"]],

    [r'(.*) Computer(.*)',
     ["Sprichst du wirklich über mich?",
      "Ist es seltsam, mit einem Computer zu sprechen?",
      "Welche Gefühle lösen Computer in dir aus?",
      "Fühlst du dich von Computern bedroht?"]],

    [r'Ist es (.*)',
     ["Denkst du, dass es {0}?",
      "Vielleicht ist es {0} -- was denkst du?",
      "Wenn es {0} wäre, was würdest du tun?",
      "Es könnte gut sein, daß es {0}."]],

    [r'Es ist (.*)',
     ["Du scheinst sehr sicher zu sein.",
      "Wenn ich dir sagte, dass es wahrscheinlich nicht {0} ist, wie würdest du dich fühlen?"]],

    [r'Kannst du ([^\?]*)\??',
     ["Warum denkst ich könnte nicht {0}?",
      "Wenn ich {0} könnte, was dann?",
      "Warum fragts du, ob ich {0} kann?"]],

    [r'Kann ich ([^\?]*)\??',
     ["Vielleicht willst du nicht {0}.",
      "Wärest du gerne in der Lage zu {0}?",
      "Wenn du {0} könntest, würdest du?"]],

    [r'Du bist (.*)',
     ["Warum denkst du das ich {0} bin?",
      "Macht es dir Freude zu denken ich wäre {0}?",
      "Vielleicht willst du, dass ich {0} bin.",
      "Vielleicht redest du in Wahrheit über dich selbst?",
      "Warum sagst du, ich wäre {0}?",
      "Warum denkst du, ich wäre {0}?",
      "Sprichst du über dich oder über mich?"]],

    [r'Ich bin nicht (.*)',
     ["Bist du nicht in Wahrheit {0}?",
      "Warum bist du nicht {0}?",
      "Willst du {0} sein?"]],

    [r'Ich fühle(.*)',
     ["Gut, erzähl mir mehr über deine Gefühle.",
      "Fühlst du oft {0}?",
      "Wann fühlst du normalerweise {0}?",
      "Wenn du fühlst {0}, was machst du dann?"]],

    [r'Ich habe (.*)',
     ["Warum erzählst du mir, dass du {0} hast?",
      "Hast du wirklich {0}?",
      "Jetzt, da du {0} hast, was machst du als nächstes?"]],

    [r'Ich würde (.*)',
     ["Kannst du erklären, warum du {0} würdest?",
      "Warum würdest du {0}?",
      "Wer weiß noch, dass du {0} würdest?"]],

    [r'Ist da (.*)',
     ["Denkst du, dass da {0} ist?",
      "Es ist wahrscheinlich, dass da {0} ist.",
      "Wärest du gern {0}?"]],

    [r'Mein (.*)',
     ["Verstehe, dein {0}.",
      "Warum sagst du, dass dein {0}?",
      "Wenn dein {0}, wie fühlst du dich?"]],

    [r'Meine (.*)',
     ["Verstehe, deine {0}.",
      "Warum sagst du, dass deine {0}?",
      "Wenn deine {0}, wie fühlst du dich?"]],

    [r'Du (.*)',
     ["Wir sollten über dich sprechen, nicht über mich",
      "Warum sagst du das über micht?",
      "Warum interessiert es dich ob ich {0}?"]],

    [r'Warum (.*)',
     ["Warum sagst du mir nicht den Grund warum {0}?",
      "Warum denkst du dass {0}?"]],

    [r'Ich will (.*)',
     ["Was würde es für dich bedeuten, wenn du {0} würdest?",
      "Warum willst du {0}?",
      "Was würdest du tun wenn du {0} würdest?",
      "Wenn du {0} bekommst, was würdest du tun?"]],

    [r'(.*) Mutter(.*)',
     ["Erzähl mir mehr über deine Mutter.",
      "Wie war die Beziehung mit deiner Mutter?",
      "Wie denkst du über deine Mutter?",
      "Wie verhält sich das zu deinen Gefühlen heute?",
      "Gute familiere Beziehungen sind wichtig."]],

    [r'(.*) Vater(.*)',
     ["Erzähl mir mehr über deinen Vater.",
      "Welche Gefühle hat dein Vater in dir ausgelöst?",
      "Wie denkst du über deinen Vater?",
      "Wie verhält sich das zu deinen Gefühlen heute?",
      "Hast du Schwierigkeiten, deiner Familie deine Gefühle zu zeigen?"]],

    [r'(.*) Kind(.*)',
     ["Hattest du enge Freunde als Kind?",
      "Was ist deine liebste Kindheitserinnerung?",
      "Erinnerst du dich an irgendwelche Träume oder Albträume aus deiner Kindheit?",
      "Haben dich die anderen Kinder manchmal geärgert?",
      "Wie denkst du, beeinflusst deine Kindheit deine heutigen Gefühle?"]],

    [r'(.*)\?',
     ["Warum fragst du das?",
      "Überleg, ob du deine Fragen selbst beantworten kannst.",
      "Vielleicht liegt die Frage in dir selbst?",
      "Sag du es mir!"]],

    [r'quit',
     ["Danke für das Gespräch.",
      "Tschüssi.",
      "Danke, das wären dann €150. Einen schönen Tag noch!"]],

    [r'(.*)',
     ["Bitte erzähl mir mehr.",
      "Lass uns ein wenig das Thema wechseln. Erzähl mir von deiner Familie.",
      "Kannst du das näher ausführen?",
      "Warum sagst du, dass {0}?",
      "Ich verstehe.",
      "Sehr interessant.",
      "{0}.",
      "Ich verstehe. Und was sagt dir das?",
      "Welche Gefühle löst das in dir aus?",
      "Wie fühlst du dich, wenn du {0} sagst?"]]
]


def reflect(fragment):
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in reflections:
            tokens[i] = reflections[token]
    return ' '.join(tokens)


def analyze(statement):
    statement = statement.capitalize()
    for pattern, responses in psychobabble:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            return response.format(*[reflect(g) for g in match.groups()])


def main():
    print("Hi. Wie geht es dir heute?")

    while True:
        statement = input(">")
        print(analyze(statement))

        if statement == "quit":
            break

if __name__ == "__main__":
    main()