# Main author: Yip
# Teacher: 駱昊
import random
from functools import total_ordering


@total_ordering
class Card:
    """one single card"""

    def __init__(self, suit, face):
        self._suit = suit
        self._face = face

    @property
    def face(self):
        return self._face

    @property
    def suit(self):
        return self._suit

    def __eq__(self, other):
        return self.face == other

    def __lt__(self, other):
        return self.face < other

    def __add__(self, other):
        return self.face + other

    def __str__(self):
        FACES = (
            None,
            "A",
            2, 3, 4, 5, 6, 7, 8, 9, 10,
            "J", "Q", "K"
        )
        return f'{self._suit}{FACES[self._face]}'

    def __repr__(self):
        return self.__str__()


class Poker:
    """deck of card"""
    def __init__(self):
        self._cards = [Card(suite, face)
                       for suite in '♠♥♣♦'
                       for face in range(1, 14)]
        self._current = 0

    @property
    def cards(self):
        return self._cards

    def shuffle(self):
        """random shuffle"""
        self._current = 0
        random.shuffle(self._cards)

    @property
    def next(self):
        """dealing cards"""
        card = self._cards[self._current]
        self._current += 1
        return card

    def __getitem__(self, item):
        return self._cards[item]


class Person(object):
    """for both dealer and players"""
    def __init__(self, name, bet):
        self._name = name
        self._cards_on_hand = []
        self._bet = bet
        self.not_bust = True
        self._21 = False

    @property
    def name(self):
        return self._name

    @property
    def cards_on_hand(self):
        return self._cards_on_hand

    @cards_on_hand.setter
    def cards_on_hand(self, value):
        self._cards_on_hand = value

    def __getitem__(self, a, b):
        return self._cards_on_hand[a:b]

    @property
    def bet(self):
        return self._bet

    @bet.setter
    def bet(self, value):
        self._bet = value

    @property
    def have21(self):
        return self._21

    @have21.setter
    def have21(self, value):
        self._21 = value

    def __truediv__(self, other):
        return self.bet / other

    def get(self, card):
        """getting cards"""
        self._cards_on_hand.append(card)

    def arrange(self, card_key):
        """arrange the card"""
        self._cards_on_hand.sort(key=card_key)

    def sum_on_hand(self, hand=None):
        total_big = 0
        ace_in = None
        for face in self._cards_on_hand:
            if face > 10:
                face = 10
            if face == 1:
                face = 11
                ace_in = True
            total_big = face + total_big
        if total_big > 21 and ace_in:
            if total_big - 10 < 21:  # take the smaller count
                return total_big - 10
            else:
                self.not_bust = False
                return False
        elif total_big > 21:
            self.not_bust = False
            return False
        else:
            return total_big

    def check_bust(self, hand=None):
        if not self.sum_on_hand(self.cards_on_hand):
            self.not_bust = False
            self.bet = 0
            return False
        elif self.sum_on_hand(self.cards_on_hand) == 21:
            print(f'{self.name} got 21!')
            self.have21 = True
            return True
        else:
            return True

    @property
    def natural_21(self):  # check whether the person got 21 in the beginning
        if self.sum_on_hand(self.cards_on_hand) == 21:
            self.have21 = True
            return True
        else:
            return False

    def clear(self):
        self.cards_on_hand.clear()
        self.not_bust = True
        self.have21 = False


class Player(Person):
    def __init__(self, name, bet=0):
        super().__init__(name, bet)
        self._second_hand = []
        self._insurance = False
        self._option = {"hit": self.hit, "stand": self.stand, "double down": self.double_down}
        self._have_split = False
        self._have_surrender = False
        self.initial_bet = bet
        self._second_not_bust = True
        self.first_not_bust = True
        self.second_bet = 0
        self.second_have21 = False

    @property
    def second_hand(self):
        return self._second_hand

    @second_hand.setter
    def second_hand(self, value):
        self.second_hand = value

    @property
    def insurance(self):
        return self._insurance

    @insurance.setter
    def insurance(self, value):
        self._insurance = value

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, value):
        self._option = value

    @property
    def second_not_bust(self):
        return self._second_not_bust

    @second_not_bust.setter
    def second_not_bust(self, value):
        self._second_not_bust = value

    @property
    def have_surrender(self):
        return self._have_surrender

    @have_surrender.setter
    def have_surrender(self, value):
        self._have_surrender = value

    @property
    def have_split(self):
        return self._have_split

    @have_split.setter
    def have_split(self, value):
        self._have_split = value

    def sum_on_hand(self, hand=None):
        if hand == self.cards_on_hand:
            total_big = 0
            ace_in = None
            for face in self.cards_on_hand:
                if face > 10:
                    face = 10
                if face == 1:
                    face = 11
                    ace_in = True
                total_big = face + total_big
            if total_big > 21 and ace_in:
                if total_big - 10 <= 21:
                    return total_big - 10
                else:
                    self.not_bust = False
                    return False
            elif total_big > 21:
                self.not_bust = False
                return False
            else:
                return total_big
        else:
            total_big = 0
            ace_in = None
            for face in hand:
                if face > 10:
                    face = 10
                if face == 1:
                    face = 11
                    ace_in = True
                total_big = face + total_big
            if total_big > 21 and ace_in:
                if total_big - 10 <= 21:
                    return total_big - 10
                else:
                    self.second_not_bust = False
                    return False
            elif total_big > 21:
                self.second_not_bust = False
                return False
            else:
                return total_big

    def check_bust(self, hand=None):
        if not self.have_split:
            if not self.sum_on_hand(hand):
                self.first_not_bust = False
                self.bet = 0
                return False
            elif self.sum_on_hand(hand) == 21:
                print(f'{self.name} got 21!')
                self.have21 = True
                return True
            else:
                return True
        else:
            if hand == self.cards_on_hand:
                if not self.sum_on_hand(hand):
                    self.first_not_bust = False
                    self.bet = 0
                    return False
                elif self.sum_on_hand(hand) == 21:
                    print(f'{self.name}\'s first hand got 21!')
                    self.have21 = True
                    return True
                else:
                    return True
            else:
                if not self.sum_on_hand(hand):
                    self._second_not_bust = False
                    self.second_bet = 0
                    return False
                elif self.sum_on_hand(hand) == 21:
                    print(f'{self.name}\'s second hand got 21!')
                    self.second_have21 = True
                    return True
                else:
                    return True

    def hit(self, card, hand):
        hand.append(card.next)
        if self.check_bust(hand) and self.have21:
            print(self)
            print("action completed\n" + "-" * 20)
            return
        elif self.check_bust(hand):
            pass
        else:
            print(f'{self.name}:\n{hand}\tbet:{self.bet}')
            return print(f'{self.name} bust!', end="\n\n")
        print(self)
        while len(hand) < 5:
            ans = input("do you want to hit once more?(yes|no):")
            if ans == "yes":
                hand.append(card.next)
                if self.check_bust(hand) and self.have21:  # if the player doesn't bust and have 21
                    print(self)
                    print("action completed\n" + "-" * 20)
                    return
                elif self.check_bust(hand):
                    print(self)
                else:  # the player busts
                    print(f'{self.name}:\n{hand}\tbet:{self.bet}')
                    print(f'{self.name} bust!\n' + "-" * 20)
                    return
            elif ans == "no":
                print("action completed\n" + "-" * 20)
                return
            else:  # second chance for careless mistake in inputting
                print("please enter a valid order, otherwise your decision will be defaulted as no")
                hit_again = input('do you want to hit once more?').lower() == 'yes'
                if hit_again:
                    hand.append(card.next)
                    if self.check_bust(hand):
                        print(self)
                    else:
                        print(f'{self.name}:\n{hand}\tbet:{self.bet}')
                        print(f'{self.name} burst!', end="\n")
                        return
                else:
                    print(self)
                    print("action completed\n", "-" * 20)
                    return
        else:
            print("you cannot hit anymore as your total card number in hand reached 5\n" + "-" * 20)
            return

    def stand(self):
        print(self)
        print("action completed\n" + "-" * 20)
        return

    def double_down(self, card, hand):
        if hand == self.cards_on_hand:
            self.bet *= 2
            hand.append(card.next)
            if self.check_bust(hand):
                print(self)
                print("action completed\n" + "-" * 20)
                return
            else:
                print(self)
                print(f'{self.name} bust!\n' + "-" * 20)
                return
        else:
            self.second_bet *= 2
            hand.append(card.next)
            if self.check_bust(hand):
                print(self)
                print("action completed\n" + "-" * 20)
                return
            else:
                print(self)
                print(f'{self.name} bust!\n' + "-" * 20)
                return

    def surrender(self):
        self.bet //= 2  # lost half of the player's bet
        self.have_surrender = True
        print(f'{self.name} has surrendered.')
        print("action completed\n" + "-" * 20)
        return

    def split(self, card):
        self.second_bet = self.bet * 1  # create another bet box
        self._have_split = True
        self.second_hand.append(self.cards_on_hand[1])
        self._cards_on_hand = self.cards_on_hand[0:1]
        print(self)
        self.cards_on_hand.append(card.next)
        self.second_hand.append(card.next)
        if self.have21 and not self.second_have21:
            print(self)
            print("-" * 20)
            print("[second hand]:\n")
            self.choice(card, self.second_hand)
        elif not self.have21 and not self.second_have21:
            print(self)
            print("-" * 20)
            print("[first hand]:\n")
            self.choice(card, self.cards_on_hand)
            print("[second hand]:\n")
            self.choice(card, self.second_hand)
        elif self.have21 and self.second_have21:
            print(self)
            print("action completed\n" + "-" * 20)
            return
        else:
            print(self)
            print("-" * 20)
            print("[first hand]:\n")
            self.choice(card, self.cards_on_hand)

    def decide_insurance(self):
        print(f'{self.name}, do you want to buy insurance(yes|no):', end="")
        want = input("")
        if want == "yes":
            self.bet *= 1.5
            self.insurance = True
        elif want == "no":
            return
        else:
            print("please enter a valid order, otherwise your decision will be defaulted as no")
            choice01 = {"yes": True, "no": False}.get(str(input("do you want to buy insurance(yes|no):")).lower(),
                                                      False)
            if choice01:
                self.bet *= 1.5
                self.insurance = True
            else:
                return

    def choice(self, card, hand):
        if not self._have_split and hand[0] == hand[1]:
            self.option.update({"split": self.split})
        if self._have_split and "split" in self.option and "surrender" in self.option:
            self.option.pop("split")
            self.option.pop("surrender")
        if (not self._have_split) and len(hand) == 2:
            self.option.update({"surrender": self.surrender})
        print(self)
        print(f'options offered for {self.name}:{list(self.option.keys())}')
        chosen = str(input("please type your decision here:")).lower()
        if chosen in {"hit", "double down"}:
            self.option[chosen](card, hand)
        elif chosen == "split" and "split" in self.option:
            self.option[chosen](card)
        elif chosen in {'stand', 'surrender'}:
            self.option[chosen]()
        else:
            print("\nplease enter a valid order, otherwise your decision will be defaulted as stand")
            print(f'options offered for {self.name}:{list(self.option.keys())}')
            chosen = input("please type your decision here:")
            if chosen in {"hit", "double down"}:
                self.option[chosen](card, hand)
            elif chosen == "split" and "split" in self.option:
                self.option[chosen](card)
            elif chosen in {'stand', 'surrender'}:
                self.option[chosen]()
            else:
                self.option["stand"]()

    def get_result(self, dealer_sum):

        def comp(a, b):  # four situation in comparing
            if a == b:
                return "draw"
            if a < b:
                return "lost"
            if a == 21:
                return "win with 21"
            return "bigger than host"

        if not self._have_split:
            return comp(self.sum_on_hand(self.cards_on_hand), dealer_sum)
        else:
            return f"{comp(self.sum_on_hand(self.cards_on_hand), dealer_sum)}|{comp(self.sum_on_hand(self.second_hand), dealer_sum)}"

    def clear(self):  # restore the default value when starting a new game
        super().clear()
        self.second_hand.clear()
        self._insurance = False
        self._option = {"hit": self.hit, "stand": self.stand, "double down": self.double_down}
        self._have_split = False
        self._have_surrender = False
        self._second_not_bust = True
        self.first_not_bust = True
        self.bet = self.bet + self.second_bet
        self.second_bet = 0
        self.second_have21 = False

    def __repr__(self):
        if len(self.second_hand) > 0:
            if self.first_not_bust and self.second_not_bust:
                return f'{self.name}:\nfirst hand:{self.cards_on_hand} second hand: {self.second_hand}\tfirst bet:{self.bet}\tsecond bet:{self.second_bet}' \
                       f'\t sum of first hand:{self.sum_on_hand(self.cards_on_hand)}\tsum of second hand:{self.sum_on_hand(self.second_hand)}'
            elif not self.first_not_bust and self.second_not_bust:
                return f'{self.name}:\nfirst hand:[bust] second hand: {self.second_hand}\tfirst bet:{self.bet}\tsecond bet:{self.second_bet}' \
                       f'\t sum of second hand:{self.sum_on_hand(self.second_hand)}'
            elif self.first_not_bust and not self.second_not_bust:
                return f'{self.name}:\nfirst hand:{self.cards_on_hand} second hand:[bust]\tfirst bet:{self.bet}\tsecond bet:{self.second_bet}' \
                       f'\t sum of first hand:{self.sum_on_hand(self.cards_on_hand)}'
            else:
                return f'{self.name}:\nfirst hand:[bust] second hand:[bust]\tfirst bet:{self.bet}\tsecond bet:{self.second_bet}'
        elif not self.not_bust:
            return f'{self.name}:\n[bust]\t bet:{self.bet}'
        else:
            return f'{self.name}:\n{self.cards_on_hand}\tbet:{self.bet}\t  sum:{self.sum_on_hand(self.cards_on_hand)}'


class Dealer(Person):
    def __init__(self, name, bet=0):
        super().__init__(name, bet)
        self._blackjack = False
        self.last = False

    @property
    def blackjack(self):
        return self._blackjack

    @blackjack.setter
    def blackjack(self, value):
        self._blackjack = value

    def get(self, card):
        self.cards_on_hand.append(card)

    @property
    def natural_21(self):
        if self.sum_on_hand == 21:
            self.blackjack = True
            return True
        else:
            return False

    @property
    def check_Ace(self):
        check = self.cards_on_hand[0]
        return check.face == 1

    def initial_secondT(self):
        check01 = self.cards_on_hand[1]
        if check01.face == 10:
            self.blackjack = True
            return True
        else:
            return False

    def clear(self):
        super().clear()
        self.blackjack = False
        self.last = False

    def __repr__(self):
        if self.blackjack or self.last:
            if self.not_bust:
                return f'{self.name}:\n{self.cards_on_hand}\tsum:{self.sum_on_hand()}'
            else:
                return f'{self.name}:\n[bust]\t'
        elif not self.not_bust:
            return f'{self.name}:\n[bust]'
        else:
            return f'{self.name}:\n[{self.cards_on_hand[0]},hidden card*{len(self.cards_on_hand) - 1}]'


# key of arranging the cards in hand
def get_key(card):
    return card.face, card.suit


def blackjack():
    p = Poker()
    p.shuffle()
    players = [Player('player 1', 100), Player('player 2', 100), Player('player 3', 100)]
    host = Dealer("host")
    game = True

    def player_get(time=1):
        for count in range(time):
            for people in players:
                people.get(p.next)

    def player_display():
        for each in players:
            each.arrange(get_key)
            print(each)

    def host_get_display():
        host.get(p.next)
        print(host)

    def all_display(time=1):
        for times in range(time):
            player_get()
            player_display()
            host_get_display()
            print("-" * 20)

    def all_clear():
        for rubbish in players:
            rubbish.clear()
        host.clear()

    def zero_bet():  # check any player has invalid bet
        for player in players:
            if player.bet <= 0:
                print(
                    f"{player.name},your bet must at least reach 100,please add your bet,otherwise your bet will be defaulted 100.")

                def inputNumber(message):
                    while True:
                        try:
                            userInput = int(input(message))
                        except ValueError:
                            print("please enter a valid number,otherwise your bet will be will be defaulted 100.")
                            continue
                        else:
                            return userInput

                want_add = inputNumber("how much do you want to add:")
                if want_add > 0 and player.bet + want_add >= 100:
                    player.bet += want_add
                else:
                    print("please enter a valid number,otherwise your bet will be will be defaulted 100.")
                    want_add01 = inputNumber("how much do you want to add:")
                    if want_add01 > 0 and player.bet + want_add01 >= 100:
                        player.bet += want_add01
                    else:
                        player.bet = 100

    def play():
        print("-" * 20)
        all_clear()  # clear the hand
        p.shuffle()  # shuffling cards
        zero_bet()  # check bet
        all_display(2)  # deal the cards to players and host
        have_21 = []
        for anyone in players:  # check who have got 21 and decide the situation
            if anyone.natural_21:
                have_21.append(anyone.name)
                anyone.have21 = True
        nonlocal game
        game = False
        if host.natural_21:  # these parts for anyone who got 21 in the beginning
            have_21.append(host.name)
        if len(have_21) > 1 and host.blackjack:  # draw
            print(f'{",".join(have_21)} have 21.')
            print("Draw")
            game = input("new game?(yes|no):").lower() == "yes"
            print()
            return
        elif host.name in have_21:  # host wins
            if host.check_Ace:  # let the players have a chance to win money if the first card of host is Ace
                player_display()
                for everyone in players:
                    everyone.decide_insurance()
                print(host)
                print("Players who bought insurance won 2 times of the insurance!")
                for have in players:
                    if have.insurance:
                        have.bet = have.bet * 5 // 3  # return the insurance and win 2 times of the insurance
                        print(f'{have.name}\'s current bet is {have.bet}:')
                game = input("new game?(yes|no):").lower() == "yes"
                print()  # for clearer display
                return
            else:  # if the first card is T, no chance.
                print(f'{host.name} has 21')
                print(f'{host.name} wins!')
                print(host)
                game = input("new game?(yes|no):").lower() == "yes"
                print()
                return
        elif host.name not in have_21 and have_21:  # player(s) win
            print()
            print(f'{",".join(have_21)} has 21')
            print(f'{",".join(have_21)} wins!Profit is 150% of his/her bet')
            for __ in players:
                if __.have21:
                    __.bet *= 2.5
                    print(f'{__.name}\'s current bet is {__.bet}:')
            game = input("new game?(yes|no):").lower() == "yes"
            print()
            return
        else:
            pass

        if host.check_Ace:  # if the host gets Ace, the host need to ask whether the players want insurance
            player_display()
            for everyone in players:
                everyone.decide_insurance()
            if host.initial_secondT():
                print(host, end="\n")
                print(host)
                print("Players who bought insurance won 2 times of the insurance!")
                for have in players:
                    if have.insurance:
                        have.bet = have.bet * 5 // 3  # return the insurance and win 2 times of the insurance
                        print(f'{have.name}\'s current bet is {have.bet}:')
                game = input("new game?(yes|no):").lower() == "yes"
                print()
                return
            else:
                print(f"{host.name}did not get a blackjack,the insurance bought is lost,game goes on.")
                print()
                for _ in players:
                    if _.insurance:
                        _.bet = _.initial_bet  # player will lose their insurance and game goes on

        for ask in players:  # ask players' decision
            ask.choice(p, ask.cards_on_hand)

        while True:  # the host will get card until he reach 17
            host.last = True
            if host.sum_on_hand() < 17 and len(host.cards_on_hand) < 5 and host.check_bust():
                print(f"{host.name} is getting...")
                host_get_display()
            elif host.sum_on_hand() >= 17 or not host.check_bust():
                print(f"{host.name} can't get anymore")
                break

        print("-" * 20)
        if not host.not_bust:  # if the host busts
            player_display()
            print(host)
            print(f'{host.name} bust!')
            print("player(s) left with blackjack won profit of 1.5 times of his/her bet,else have 1 times")
            for left in players:
                if not left.have_split:  # for those who didn't split
                    if left.have21:
                        left.bet *= 2.5
                        print(f'{left.name}\'s current bet:{left.bet}')
                    elif left.not_bust:
                        left.bet *= 2
                        print(f'{left.name}\'s current bet:{left.bet}')
                    print("-" * 20)
                else:
                    if left.have21:
                        left.bet *= 2.5
                        print(f'{left.name}\'s current first bet:{left.bet}')
                    elif left.not_bust:
                        left.bet *= 2
                        print(f'{left.name}\'s current first bet:{left.bet}')
                    if left.second_have21:
                        left.second_bet *= 2.5
                        print(f'{left.name}\'s current second bet:{left.second_bet}')
                    elif left.second_not_bust:
                        left.second_bet *= 2
                        print(f'{left.name}\'s current second bet:{left.second_bet}')
                    print("-" * 20)
                game = input("new game?(yes|no):").lower() == "yes"
                print()
                return

        win_with_21 = []  # four situations if the host didn't bust
        bigger_than_host = []
        lost = []
        draw = []
        result = {"win_with_21": "player(s) left with blackjack won profit of 1.5 times of his/her bet ",
                  "bigger_than_host": "player(s) who win host without 21 won profit of 1 times of his/her bet",
                  "lost": "player(s) who lost host without 21 lost his/her bet",
                  "draw": "player(s) who got a draw have their bet return"}  # description of result

        for winner in players:
            if not winner.have_surrender and not winner.have_split:  # for player who didn't surrender and didn't split
                situation = winner.get_result(host.sum_on_hand())
                if situation == "win with 21":
                    winner.bet *= 2.5
                    win_with_21.append(winner.name)
                elif situation == "bigger than host":
                    winner.bet *= 2
                    bigger_than_host.append(winner.name)
                elif situation == "draw":
                    draw.append(winner.name)
                else:
                    winner.bet = 0
                    lost.append(winner.name)
            elif not winner.have_surrender and winner.have_split:  # for player who have split and didn't surrender
                situation01 = (winner.get_result(host.sum_on_hand()).split("|"))[0]
                situation02 = (winner.get_result(host.sum_on_hand()).split("|"))[1]
                if situation01 == "win with 21":  # the situation for first hand
                    winner.bet *= 2.5
                    win_with_21.append(f'{winner.name}\'s first hand')
                elif situation01 == "bigger than host":
                    winner.bet *= 2
                    bigger_than_host.append(f'{winner.name}\'s first hand')
                elif situation01 == "draw":
                    draw.append(f'{winner.name}\'s first hand')
                else:
                    winner.bet = 0
                    lost.append(f'{winner.name}\'s first hand')

                if situation02 == "win with 21":  # the situation for second hand
                    winner.second_bet *= 2.5
                    win_with_21.append(f'{winner.name}\'s second hand')
                elif situation02 == "bigger than host":
                    winner.second_bet *= 2
                    bigger_than_host.append(f'{winner.name}\'s second hand')
                elif situation02 == "draw":
                    draw.append(f'{winner.name}\'s second hand')
                else:
                    winner.second_bet = 0
                    lost.append(f'{winner.name}\'s second hand')
            else:
                pass
        print("calculating result...\n" + "-" * 20)  # just for fun
        print(result["win_with_21"] + ":\n" + ",".join(win_with_21))
        print(result["bigger_than_host"] + ":\n" + ",".join(bigger_than_host))
        print(result["lost"] + ":\n" + ",".join(lost))
        print(result["draw"] + ":\n" + ",".join(draw))
        print("-" * 20)
        player_display()
        print(host)
        game = input("new game?(yes|no):").lower() == "yes"
        print()
        return

    while game:
        play()


if __name__ == '__main__':
    blackjack()
