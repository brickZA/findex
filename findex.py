from ankiqt import ui, mw
from anki import utils, deck
from anki.hooks import wrap
from math import log
from PyQt4 import QtGui, QtCore
import os

from fi import fiui

VERSION = 0.1; DATE = '2011-05-29'
CHANGELOG = '''\
Version 0.1 2011-05-29
* Initial release
'''

RULEDELIM = '::'
WILDCARD = '*'
DEFAULTFI = 10
COMMENTMARK = '#'

VERBOSE = False

CONFIGFILE = 'findex.config'
configpath = os.path.join(mw.config.configPath, CONFIGFILE)

ICONPATH = os.path.join(mw.pluginsFolder(), 'fi', 'forgetting.png')

WEBPAGE = 'http://mesha.org/anki/plugins.html'

# http://www.flickr.com/photos/-cavin-/2771404615/

# rule format:
# deck :: tag(s) :: condition :: new FI (:: assumed old FI)
myrules = '''
main-copy :: * :: mature :: 25
main-copy :: * :: young :: 10 :: 20
'''

DEFAULTRULES = '''
# Put rules here for changing the forgetting index of specific cards
# Rule format:
# deck :: tag(s)/model :: condition :: FI (:: original FI)
# See help for more details
# Example: Change the forgetting index for all cards to 5%
# * :: * :: * :: 5%'''

HELP = '''\
The forgetting index is the percentage of cards that you have forgotten when it is time to review them.
Anki s default algorithm has a forgetting index of about 10%, though it depends greatly on the person,
the material, how well the material is formulated, etc. The actual retention rate is higher than
the forgetting index, because the forgetting index is measured only when a card comes up for review,
although at any given time you are only part of the way through the scheduled interval for most
cards. This plugin allows you to change the forgetting index for specific cards or groups of cards.

The configuration for the forgetting index is a list of rules to match cards,
and what forgetting index to change the cards to if they do match. Each line
consists of four or five fields, separated by two colons (::).

The first field is the deck. You can use an asterisk (*) to indicate that the rule applies
to any deck.

The second field is the model or a list of tags that the card must have. Again you can use an asterisk
(*) to indicate any tag or model.

The third field allows you to set some other conditions. At present it can only be one of the words,
'new', 'young', or 'mature', to indicate that the card must have that state, or an asterisk (*) to
indicate that the condition does not matter and the rule will apply to any card.

The fourth field has the forgetting index itself, expressed as a percent. The percent sign (%) is
optional.

The fifth field is optional, but if it is given, it indicates the assumed original (unmodified)
forgetting index. If unspecified, it is assumed to be {defaultfi}%. Thus if you find that for a
certain set of cards your effective forgetting index is 8%, and you would like to lower it to 3%,
you can put 8% in the fifth field and 3% in the fourth. This is mathematically equivalent to
changing the forgetting index from 10% to about 3.78%, but is easier to specify if you know
your effective forgetting index for a group of cards.

Any line beginning with a hash (#) is treated as a comment and is ignored.

The <b>last</b> rule that matches a given card is the one that will be used to set its forgetting
index. Therefore, put your general, default rules near the top and more specific rules near the bottom.

NOTE: This plugin does not put any limits on the forgetting index values that you specify,
and will happily allow you to specify all kinds of strange and inefficient things. If you specify
a forgetting index below 3%, reviews will start to occur annoyingly often with very little increase
in retention. A forgetting index above 20%-30% will result in wasted time due to the need to relearn
forgotten items.

A forgetting index of 0% logically implies that the next repetition should always be right away, and
so it is disallowed.

<i>Examples</i>

To globally change the forgetting index for all cards to 5%, use:

<blockquote>* :: * :: * :: 5%</blockquote>

To change cards with a 'sentence' tag in the Japanese deck to have a forgetting index of
15%, use:

<blockquote>Japanese :: sentence :: * :: 15%</blockquote>

If you find that your actual measured forgetting index for young cards is 20%, and you would
like to lower that to 10%, use:

<blockquote>* :: * :: young :: 10% :: 20%</blockquote>

For more information on forgetting indexes and forgetting curves see:

<ul>
<li>Supermemo: Forgetting index: <a href="http://www.supermemo.com/help/fi.htm">http://www.supermemo.com/help/fi.htm</a></li>
<li>Forgetting curve on Wikipedia: <a href="http://en.wikipedia.org/wiki/Forgetting_curve">http://en.wikipedia.org/wiki/Forgetting_curve</a></li>
</ul>

<i>Version {version}, released {date}. Written by Adam Mesha &lt;adam@mesha.org&gt;.
Released under the GNU GPL v3.
<a href="{webpage}">{webpage}</a>. Icon based on the image at
<a href="http://www.flickr.com/photos/-cavin-/2771404615/">http://www.flickr.com/photos/-cavin-/2771404615/</a></i>
'''.format(defaultfi=DEFAULTFI, webpage=WEBPAGE, version=VERSION, date=DATE)

HELP = '\n\n'.join(['<p>'+para+'</p>' for para in HELP.split('\n\n')])

def getnum(s):
    if hasattr(s, 'strip'):
        s = s.strip('%')
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None

class MatchRules(object):
    def __init__(self, rules=None):
        if rules is not None:
            self.setrules(rules)
    def setrules(self, ruletext):
        self.ruletext = ruletext
        self.rules = []
        for rule in ruletext.split('\n'):
            rule = rule.strip()
            if rule and not rule.startswith(COMMENTMARK):
                self.addrule(rule)
        with open(configpath, 'w') as f:
            f.write(ruletext)
    def readconfig(self):
        if not os.path.exists(configpath):
            self.setrules(DEFAULTRULES)
        else:
            with open(configpath, 'r') as f:
                self.setrules(f.read())
    def addrule(self, s):
        fields = [i.strip() for i in s.split(RULEDELIM)]
        if len(fields) == 4:
            deck, tags, condition, newfi = fields
            oldfi = DEFAULTFI
        elif len(fields) == 5:
            deck, tags, condition, newfi, oldfi = fields
        else:
            ui.utils.showInfo('Invalid forgetting index rule: \n {0}'.format(s))
        newfi = getnum(newfi)
        oldfi = getnum(oldfi)
        if newfi is None or oldfi is None or newfi <= 0 or oldfi <= 0:
            ui.utils.showInfo('Invalid forgetting index rule: \n {0}'.format(s))
            return
        self.rules.append((deck, tags, condition, newfi, oldfi))
    @staticmethod
    def matches(rule, card):
        deck, tags, condition, newfi, oldfi = rule
        if deck != WILDCARD:
            if card.deck.name() != deck:
                return False
        if tags != WILDCARD:
            tags = utils.parseTags(tags)
            cardtags = card.allTags()
            for tag in tags:
                if not utils.findTag(tag, cardtags):
                    return False
        if condition != WILDCARD:
            cardstate = card.deck.cardState(card)
            if cardstate != condition:
                return False
                # XXX soup up the possible conditions
        return True
    def getfi(self, card):
        for rule in reversed(self.rules):
            if self.matches(rule, card):
                return rule[-2]/100.0, rule[-1]/100.0
        return None, None

firules = MatchRules()
firules.readconfig()
getfi = firules.getfi

def reschedule(t, f, F):
    '''Reschedule a repetition scheduled in t days so that it has a forgetting index of f
    with original forgetting index of F.
    Based on the formula R = e**-(t/S), where R is retention, S is memory strength, and t is time.
    http://en.wikipedia.org/wiki/Forgetting_curve'''
    R = 1 - F # original retention index
    r = 1 - f # desired retention index
    return t * log(r) / log(R)

def newNextInterval(self, card, ease, _old):
    orig = _old(self, card, ease)
    if orig == 0:
        return orig
    newfi, oldfi = getfi(card)
    if newfi is None:
        return orig
    return reschedule(orig, newfi, oldfi)

oldnextival = deck.Deck.nextInterval
deck.Deck.nextInterval = wrap(deck.Deck.nextInterval, newNextInterval, 'around')

# add a 'forgetting index' item to card stats

from anki import stats
OldCardStats = stats.CardStats

class FICardStats(OldCardStats):
    def report(self):
        fi, oldfi = getfi(self.card)
        if fi is None:
            fi = 'default'
        else:
            fi = '{0}%'.format(int(fi*100))
        if oldfi is not None and int(oldfi*100) != DEFAULTFI:
            oldfi = '{0}%'.format(int(oldfi*100))
        else:
            oldfi = None
        txt = OldCardStats.report(self)
        if not self.txt.endswith('</table>'):
            return self.txt
        self.txt = self.txt[:-8]
        self.addLine('Forgetting index', fi)
        if oldfi is not None:
            self.addLine('Original FI', oldfi)
        if VERBOSE:
            for i in range(1, 5):
                self.addLine('Orig interval for {0}'.format(i), '{0:.2f}'.format(
                                                oldnextival(self.deck, self.card, i)))
        self.txt += '</table>'
        return self.txt

stats.CardStats = FICardStats

# configuration GUI

def gethelp():
    ui.utils.showText(HELP, type='html')

def showconfig():
    d = QtGui.QDialog(mw)
    d.setWindowIcon(QtGui.QIcon(ICONPATH))
    form = fiui.Ui_fidialog()
    form.setupUi(d)
    form.plainTextEdit.setPlainText(firules.ruletext)
    QtCore.QObject.connect(form.buttonBox, QtCore.SIGNAL("helpRequested()"), gethelp)
    ret = d.exec_()
    if not ret:
        return
    firules.setrules(unicode(form.plainTextEdit.toPlainText()))

mw.mainWin.FI = QtGui.QAction('Set forgetting indexes', mw)
mw.mainWin.FI.setStatusTip('Set forgetting indexes')
mw.mainWin.FI.setEnabled(True)
mw.mainWin.FI.setIcon(QtGui.QIcon(ICONPATH))
mw.connect(mw.mainWin.FI, QtCore.SIGNAL('triggered()'), showconfig)
mw.mainWin.menu_Settings.addAction(mw.mainWin.FI)

mw.registerPlugin("Forgetting indexes", 20110520)
