from DraftRecommander import DraftRecommander
import sys

DR = DraftRecommander()
DR.GetData()
DR.GetPlayers()
while True:
    sys.stdout.write('>> ')
    command = raw_input()
    if  command == 'o':         #others
        sys.stdout.write("Player name or dump others stats (name or 'd'): >> ")
        newDrafted = raw_input()
        if newDrafted == 'd':
            DR.DumpStats('others')
        else:
            try:
                DR.PutDraftedPool(newDrafted, 'others')
            except:
                print 'No such player'
    elif command == 'm':       #me
        DR.Recommand()
        sys.stdout.write("Player name or dump others stats (name or 'd'): >> ")
        newDrafted = raw_input()
        if newDrafted == 'd':
            DR.DumpStats('my')
        else:
            try:
                DR.PutDraftedPool(newDrafted, 'me')
            except:
                print 'No such player'
    else:
        print "Invalid command"
