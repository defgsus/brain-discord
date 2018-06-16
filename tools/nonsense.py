import random

REPLIES = [
    "Ja %s",
    "Nein %s",
    "Danke %s",
    "Meine Güte, %s",
    "Moment %s",
    "%s, es ist doch so",
    "Was %s sagt, hat Hand und Fuß, aber",
    "Wer will %s widersprechen? Dennoch",
]


class NonsenseGenerator:
    def __init__(self, name, srt_file, encoding, avatarfile, names, auto_concat=False, max_lines=6):
        self.name = name
        self.max_lines = max_lines
        self._names = names

        if not isinstance(avatarfile, (list, tuple)):
            avatarfile = [avatarfile]
        self.avatarfiles = avatarfile
        self._avatar = None

        with open(srt_file, encoding=encoding) as f:
            text = f.read()

        # split into lines
        lines = [(" ".join([y.replace("- ", "").replace("<i>", "").replace("</i>", "").strip()
                            for y in x.split("\n")[2:]])).strip()
                      for x in text.split("\n\n")][:-2]
        lines = [l for l in lines if l]

        # concat half-sentences
        if auto_concat:
            self.lines = []
            lastline = "."
            for l in lines:
                if lastline[-1] not in (".", "?", "!"):
                    self.lines[-1] += " " + l
                else:
                    self.lines.append(l)
                lastline = self.lines[-1]
        else:
            self.lines = lines

        # get indices for lines with known names
        self.names_idx = [i for i, l in enumerate(self.lines) if self._has_name(l)]

        self.linesmap = {}
        self.namesmap = {}

    @property
    def avatar(self):
        if len(self.avatarfiles) == 1 and self._avatar is not None:
            return self._avatar
        fn = self.avatarfiles[random.randrange(len(self.avatarfiles))]
        with open(fn, "rb") as f:
            self._avatar = f.read()
        return self._avatar

    def _rand_choice(self, seq):
        return seq[random.randrange(len(seq))]

    def rand_range(self, length, countmap):
        bestidx = 0
        bestcnt = -1
        for i in range(5):
            idx = random.randrange(length)
            cnt = countmap.get(idx, 0)
            if bestcnt < 0 or cnt < bestcnt:
                bestidx = idx
                bestcnt = cnt
        countmap[bestidx] = bestcnt+1
        return bestidx

    def _has_name(self, line):
        for n in self._names:
            if n in line:
                return True
        return False

    def _replacenames(self, line, names):
        names = [n[:1].upper() + n[1:] for n in names]
        for n in self._names:
            line = line.replace(n, self._rand_choice(names))
        return line

    def _endtoken(self, t):
        return t[-1] in (".", "!", "?") or t.lower() == "brian"

    def rand(self, num=0, names_repl=None, choose_name_lines=False):
        if num == 0:
            num = random.randint(1, random.randint(1, self.max_lines))
        if choose_name_lines:
            idx = self.rand_range(len(self.names_idx), self.namesmap)
            idx = self.names_idx[idx]
        else:
            idx = self.rand_range(len(self.lines), self.linesmap)
        lines = self.lines[idx:idx+num]
        idx += num
        while not self._endtoken(lines[-1]) and idx < len(self.lines):
            line = self.lines[idx]
            lines.append(line)
            idx += 1
        for x in ("Amen",):
            lines2 = lines
            lines = []
            for line in lines2:
                lines.append(line)
                if x.lower() in line.lower() or x.endswith("?"):
                    break
        if names_repl:
            lines = [self._replacenames(x, names_repl) for x in lines]

        return "\n".join(lines)

    def rand_reply(self, user_name, names, choose_name_lines=False, num=0):
        rep = self.rand(num, names, choose_name_lines)
        rep = rep[0].lower() + rep[1:]
        return "%s, %s" % (self._rand_choice(REPLIES) % user_name, rep)


class LifeOfBrian(NonsenseGenerator):
    def __init__(self):
        super(LifeOfBrian, self).__init__(
            "Brian",
            "./subtitles/das-leben-des-brian.srt", "latin1",
            "./subtitles/pilatus_trans.png",
            ["Brian", "Bwian", "Judith", "Pilatus", "Reg", "Jesus", "Stan", "Loretta", "Matthias",
             "Schwanzus", "Meister", "Frank", "Boris", "Judäisch", "Zenturio", "Dicknase", "Poback",
             "Francis", "Goliath", "Wache", "Bruder", "Schwester", "Samariter", "Cäsar", "Judäa",
             "Jehova", "Dämon", "Gotte", "Gott", "Messias", "Herr", "Römer", "Mama", "Mutter"],
            max_lines=6,
        )


class BladeRunner(NonsenseGenerator):
    def __init__(self):
        super(BladeRunner, self).__init__(
            "Rachael",
            "./subtitles/bladerunner.srt", "utf-8",
            ("./subtitles/rachael.png", "./subtitles/rachael2.png"),
            ["Tyrell", "Gaff", "Eddie", "J. F. Sebastian", "J.F.", "Taffey Lewis", "Taffey", "Rachael", "Sebastian",
             "Deckard", "Bryant", "Springer", "Dame", "Läufer", "Holden", "Kumpel", "Leon",
             "Vater", "Roy Batty", "Roy", "Pris", "Zhora", "Replikant", "Ork", "Prosser", "Ankovitch",
             "Salome", "Chew", "Abdul Hassan", "Hautjob"],
            auto_concat=True,
            max_lines=3,
        )


class ExtraTerrestrial(NonsenseGenerator):
    def __init__(self):
        super(ExtraTerrestrial, self).__init__(
            "E.T.",
            "./subtitles/et.srt", "utf-8",
            "./subtitles/et.png",
            ["Elliott", "Mama", "Mami", "E.T.", "Mike", "Gertie", "Michael", "Tyler", "Mary",
             "Greg", "Kojote", "Kobold", "Peter", "Kerl", "Steve", "Harvey", "Lou", "Ralf"],
            auto_concat=True,
            max_lines=4,
        )


NONSENSE_GENERATORS = {
    "life": LifeOfBrian(),
    "bladerunner": BladeRunner(),
    "e.t.": ExtraTerrestrial(),
}


if __name__ == "__main__":

    g = LifeOfBrian()
    #g = BladeRunner()
    #g = ExtraTerrestrial()

    for i in range(100):
        #print("-\n" + g.rand())
        print("-\n" + g.rand_reply(user_name="Boris", names=["Anton", "Emil", "Paul"]))

