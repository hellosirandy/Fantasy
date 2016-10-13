from DraftRecommander import DraftRecommander
import sys

DR = DraftRecommander()
DR.GetData()
DR.GetPlayers()
while True:
    sys.stdout.write('Identity: (o or m) >> ')
    identity = raw_input()
    if  identity == 'o':         #others
        try:
            sys.stdout.write('Player name: >> ')
            newDrafted = raw_input()
            DR.PutDraftedPool(newDrafted, 'others')
        except:
            print 'No such player'
    elif identity == 'm':       #me
        DR.Recommand()
        try:
            sys.stdout.write('Player name: >> ')
            newDrafted = raw_input()
            DR.PutDraftedPool(newDrafted, 'me')
        except:
            print 'No such player'
    else:
        print "Please insert 'o' or 'm'"
