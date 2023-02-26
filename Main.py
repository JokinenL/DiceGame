"""
Otetaan käyttöön kirjastot tkinter, random ja time. Niitä käytetään myöhemmin ohjelmassa. IMAGE_FILES-listaan on tallennettu noppien kuvatiedostojen nimet.
POSSIBLE_BETS-listaan on tallennettu käytössä olevat panokset. PAYOUT_RATIOS-dictiin on tallennettu jokaisen voittavan käden voittokerroin. Nämä on toteutettu
globaaleina muuttujina, sillä ne pysyvät aina vakiona ja näin niitä voidaan käyttää helposti eri funktioissa/metodeissa ilman parametreillä pelaamista.
"""
from tkinter import *
import random
import time

IMAGE_FILES = ["Images\Dice_1.gif", "Images\Dice_2.gif", "Images\Dice_3.gif", "Images\Dice_4.gif",
               "Images\Dice_5.gif", "Images\Dice_6.gif"]

POSSIBLE_BETS = [0.50, 1.00, 1.50, 2.00]

PAYOUT_RATIOS = {'Two pair' : 0.5, 'Three of a kind' : 0.5, 'Low straight' : 1.5,
                 'High straight' : 2, 'Full house' : 2.5, 'Four of a kind' : 3, 'Five of a kind' : 5}

class Dice_game:

    """
    Koko peli perustuu Dice_game-luokan ympärille. Kaikki pelissä tapahtuva suoritetaan tämän luokan metodien avulla.
    """

    def __init__(self):
        """
        Rakentajametodissa määritellään ensiksi kaikki luokan attribuutit (napit, labelit ja kuvat) ja sen jälkeen asetellaan ne oikeille paikoilleen ikkunassa.
        Attribuutteja on sen verran paljon, että selkeyden vuoksi niiden mahdolliset selitykset on esitetty #-kommentteina koodin seassa eikä jokaista yksitellen
        näissä docstringeissä.
        """

        self.__main_window = Tk()
        self.__main_window.title("Dice Game")
        self.__main_window.option_add("*Font", "Verdana 16")

        # Alustetaan lista, johon alla olevassa for-silmukassa tallennetaan noppien kuvat.
        self.__dice_images = []

        for image in IMAGE_FILES:
            new_photo = PhotoImage(file=image)
            self.__dice_images.append(new_photo)

        #Luodaan kehys, jonka sisälle painikkeet ja labelit myöhemmin asetellaan.
        self.__main_frame = Frame(self.__main_window, bg="grey")

        self.__starting_image = PhotoImage(file="Images\Dice_1.gif")

        #Kaikki nopat asetetaan aluksi silmäluvulle 1.
        self.__dice_1 = Label(self.__main_frame, image=self.__starting_image)
        self.__dice_2 = Label(self.__main_frame, image=self.__starting_image)
        self.__dice_3 = Label(self.__main_frame, image=self.__starting_image)
        self.__dice_4 = Label(self.__main_frame, image=self.__starting_image)
        self.__dice_5 = Label(self.__main_frame, image=self.__starting_image)

        #Luodaan kaikille nopille nappi, jolla ne saa pidettyä paikoillaan heittojen välissä.
        self.__hold_button_1 = Button(self.__main_frame, text="HOLD", command=lambda: self.hold_dice(self.__dice_1), bg="red", fg="black")
        self.__hold_button_2 = Button(self.__main_frame, text="HOLD", command=lambda: self.hold_dice(self.__dice_2), bg="red", fg="black")
        self.__hold_button_3 = Button(self.__main_frame, text="HOLD", command=lambda: self.hold_dice(self.__dice_3), bg="red", fg="black")
        self.__hold_button_4 = Button(self.__main_frame, text="HOLD", command=lambda: self.hold_dice(self.__dice_4), bg="red", fg="black")
        self.__hold_button_5 = Button(self.__main_frame, text="HOLD", command=lambda: self.hold_dice(self.__dice_5), bg="red", fg="black")

        #Luodaan dict, johon tallennetaan kaikki ohjelman tarvitsema tieto nopista. Nopan numerolla löydetään dictistä lista, jossa on järjestyksessä 1. nopan arvo
        #2. noppaa säätelevä painike ja 3. nopan paikallaan pitämiseen liittyvä totuusarvo, jota tervitaan hold_dice-metodissa. Alkutilanteessa jokaisen nopan arvo on
        #1, eikä niitä voi lukita (hold), sillä totuusarvo on False.
        self.__dice_data = {self.__dice_1:[1, self.__hold_button_1, False], self.__dice_2:[1, self.__hold_button_2, False],
        self.__dice_3:[1, self.__hold_button_3, False], self.__dice_4:[1, self.__hold_button_4, False],
        self.__dice_5:[1, self.__hold_button_5, False]}

        #Kaikki panokseen liittyvät napit ja labelit on määritelty tässä. Bet_counteri toimii change_bet-metodin kanssa yhdessä siten, että panosta voi nappia
        #painamalla aina muuttaa seuraavaan arvoon. Change_bet-metodia kutusutaan käyttäjän painaessa bet_buttonia.
        self.__bet_counter = 0
        self.__bet_value = POSSIBLE_BETS[self.__bet_counter]
        self.__bet_text = Label(self.__main_frame, text="BET: ", bg="black", fg="white")
        self.__bet_button = Button(self.__main_frame, text="BET", command=self.change_bet, bg="red")
        self.__bet_label = Label(self.__main_frame, text=f"{self.__bet_value:.2f}", bg="black", fg="white")

        #Tässä määritellään heittonappi ja heittolaskuri. Heittolaskurin tarkoitus on kertoa ohjelmalle, onko meneillään pelin ensimmäinen vai toinen heitto. Tämä
        #vaikuttaa siihen, onko noppien lukitseminen tai manoksen muuttaminen mahdollista ja määrittää sen, otetaanko pelivarauksista maksu heittonappia painettaessa.
        #Huoioitavaa on, että throw-counterin arvo nolla vastaa tilannetta, jossa pelin jälkimmäinen heitto on tehty. Laskuri siis vaihtelee arvojen 0 ja 1 välillä.
        #Saavutettuaan arvon 2 se palautetaan takaisin nollaan.
        self.__throw_button = Button(self.__main_frame, text="THROW", command=self.throw, bg="red")
        self.__throw_counter = 0

        #Stop_button lopettaa ohjelman suorituksen.
        self.__stop_button = Button(self.__main_frame, text="CLOSE", command=self.quit, bg="black", fg="white")

        #Tässä määritellään voittotaulu.
        self.__paytable_image = PhotoImage(file="Images\Pay_table.GIF")
        self.__paytable_label = Label(self.__main_frame, image=self.__paytable_image)

        #Tässä määritellään pelivarausten arvo ja labelit, joista käyttäjä saa arvon luettua.
        self.__credits_value = 0
        self.__credits_text = Label(self.__main_frame, text="CREDITS: ", bg="black", fg="white")
        self.__credits_label = Label(self.__main_frame, text=f"{self.__credits_value:.2f}", bg="black", fg="white")

        #Tässä määritellään pelivarausten syöttämiseen liittyvät napit, tekstikentät ja painikkeet. Käyttäjä kirjoittaa tekstikenttään (entry) kuinka paljon
        #pelivarauksia hän haluaa tallettaa, ja painaa insert_credits_buttonia, jolloin kututaan metodia insert_credits, jossa talletus tapahtuu.
        self.__insert_credits_text = Label(self.__main_frame, text="INSERT CREDITS: ", bg="black", fg="white")
        self.__insert_credits_entry = Entry(self.__main_frame, bg="black", fg="white")
        self.__insert_credits_button = Button(self.__main_frame, text="PRESS TO INSERT", command=self.insert_credits, bg="grey", fg="black")

        #Viimeiseksi määritellään infoboxi, johon kaikki käyttäjälle annettavat ohjeet kijoitetaan. Kaksi tyhjää tekstiriviä on määritelty ikkunan
        #asettelua varten. Niitä käytetään alla asettelun yhteydessä.
        self.__info_box = Label(self.__main_frame, text="INSERT CREDITS TO PLAY", bg="black", fg="white")
        self.__empty_row_1 = Label(self.__main_frame, text="", bg="grey")
        self.__empty_row_2 = Label(self.__main_frame, text="", bg="grey")


        #ASETTELU

        self.__main_frame.grid(row=0, column=0)

        self.__paytable_label.grid(row=0, column=0, columnspan=12)

        self.__info_box.grid(row=1, column=0, columnspan=12)

        self.__dice_1.grid(row=2, column=1)
        self.__dice_2.grid(row=2, column=2)
        self.__dice_3.grid(row=2, column=3)
        self.__dice_4.grid(row=2, column=4)
        self.__dice_5.grid(row=2, column=5)

        self.__hold_button_1.grid(row=3, column=1)
        self.__hold_button_2.grid(row=3, column=2)
        self.__hold_button_3.grid(row=3, column=3)
        self.__hold_button_4.grid(row=3, column=4)
        self.__hold_button_5.grid(row=3, column=5)

        self.__empty_row_1.grid(row=4, column=0)

        self.__credits_text.grid(row=5, column=0)
        self.__credits_label.grid(row=5, column=1)
        self.__throw_button.grid(row=5, column=10)

        self.__bet_text.grid(row=6, column=0)
        self.__bet_label.grid(row=6, column=1)
        self.__bet_button.grid(row=6, column=10)

        self.__empty_row_2.grid(row=7, column=0)

        self.__insert_credits_text.grid(row=8, column=9)
        self.__insert_credits_entry.grid(row=8, column=10)

        self.__stop_button.grid(row=9, column=0)
        self.__insert_credits_button.grid(row=9, column=10)



    def throw(self):
        """
        Metodi suoritetaan, kun pelaaja painaa heittonappia (throw_button). Noppia voi heittää vaan, jos pelivaraukset riittävät uuden pelin aloittamiseen tai peli on
        kesken (throw_counter == 1). Muuten pelaajaa ohjeistetaan joko pienentämään panostaan tai tallettamaan lisää pelivarauksia. Varsinaisen heiton aikana nopille
        arvotaan sattuman varaisesti uusi arvo väliltä [1,6]. Kun pelin jälkimmäinen heitto on heitetty (throw_counter > 1) suoritetaan metodit check_winnings, joka
        tarkistaa tuliko voittoa ja suorittaa voitonmaksun, ja reset, joka nollaa tarvittavat atribuuttien arvot uutta peliä varten.

        """
        if self.__credits_value >= self.__bet_value or self.__throw_counter == 1:
            if self.__throw_counter == 0:
                self.__credits_value -= self.__bet_value
                self.__credits_label.configure(text=f"{self.__credits_value:.2f}", bg="black", fg="white")

            self.__throw_counter += 1


            for dice in self.__dice_data:
                #Tässä tarkastetaan, onko noppa lukittu.
                if not self.__dice_data[dice][2]:

                    for dice_spin in range(0, 5):
                        dice_value = random.randint(1, 6)
                        dice.configure(image=self.__dice_images[dice_value - 1])
                        self.__main_window.update_idletasks()
                        time.sleep(0.05)

                    self.__dice_data[dice][0] = dice_value

            if self.__throw_counter > 1:
                self.check_winnings()
                self.reset()

            if self.__throw_counter == 1:
                self.__info_box.configure(text="WHICH DICES YOU WANT TO HOLD?")

        elif self.__credits_value <= 0.25:
            self.__info_box.configure(text="INSERT CREDITS TO PLAY")

        else:
            self.__info_box.configure(text="LOWER YOUR BET TO PLAY")



    def insert_credits(self):
        """
        Metodia kutsutaan painamalla INSERT-painiketta ikkunan oikeassa alareunassa. Tällöin yritetään syöttää lisää pelivarauksia tekstikenttään insert_credits_entry
        syötetty määrä. Metodi tarkastaa, että käyttämän antama syöte on kelvollinen ja virhetilanteessa se ohjeistaa, mitä tekstikenttään kuuluu syöttää.

        """

        try:
            if float(self.__insert_credits_entry.get()) > 0 and float(self.__insert_credits_entry.get()) % 0.25 == 0:
                self.__credits_value += float(self.__insert_credits_entry.get())

                if self.max_credits():
                    self.__info_box.configure(text="MAX AMOUNT OF CREDITS IS 1000")

                else:
                    self.__credits_label.configure(text=f"{self.__credits_value:.2f}", bg="black", fg="white")
                    self.__insert_credits_entry.delete(0,END)
                    self.__info_box.configure(text="PRESS THE THROW BUTTON TO PLAY")

            else:
                self.__info_box.configure(text="CREDITS TO INSERT MUST BE A POSITIVE NUMBER DIVISIBLE BY 0.25")
                self.__insert_credits_entry.delete(0,END)


        except ValueError:
            if self.__insert_credits_entry.get() == "":
                self.__info_box.configure(text="HOW MUCH CREDITS YOU WANT TO INSERT?")
            else:
                self.__info_box.configure(text="CREDITS TO INSERT MUST BE A POSITIVE NUMBER DIVISIBLE BY 0.25")
                self.__insert_credits_entry.delete(0,END)


    def change_bet(self):
        """
        Metodia kutsutaan, kun pelaaja haluaa muuttaa panostaan. Panosta voi vaihtaa ennen uuden pelin aloittamista (throw_counter == 0). Jos käyttäjä yrittää
        vaihtaa panosta kesken pelin, kirjoitetaan infokenttään virheilmoitus. Käytännössä panosta vaihdetaan käymällä läpi listan POSSIBLE_BETS arvoja järjestyksessä.
        """
        if self.__throw_counter == 0:

            if POSSIBLE_BETS[self.__bet_counter] < 2.00:
                self.__bet_counter += 1

            else:
                self.__bet_counter = 0

            self.__bet_value = POSSIBLE_BETS[self.__bet_counter]
            self.__bet_label.configure(text=f"{self.__bet_value:.2f}")

        else:
            self.__info_box.configure(text="THROW AGAIN BEFORE CHANGING THE BET")


    def hold_dice(self, dice_to_hold):
        """
        Metodi suoritetaan, kun käyttäjä painaa HOLD-nappia jonkun nopan alapuolella. Tällöin kyseinen noppa lukitaan, eli lukitsemisesta kertovaksi
        totuusarvoksi muutetaan True ja painike vaihtaa väriään lukitsemisen merkiksi. Metodi ottaa parametrinään sen nopan, joka halutaan lukita. Noppa
        voidaan lukita vain pelin ensimmäisen ja toisen heiton välissä (throw_counter == 1). Metodi toimii myös käänteiseen suuntaan, eli painamalla HOLD-nappia
        uudelleen lukitus poistuu.
        """

        if self.__throw_counter == 1:

            if self.__dice_data[dice_to_hold][2]:
                self.__dice_data[dice_to_hold][2] = False
                self.__dice_data[dice_to_hold][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(dice_to_hold))

            else:
                self.__dice_data[dice_to_hold][2] = True
                self.__dice_data[dice_to_hold][1].configure(text="HOLD", bg="black", fg="white", command=lambda: self.hold_dice(dice_to_hold))

    def check_winnings(self):
        """
        Metodia kutsutaan aina pelin jälkimmäisen heiton jälkeen throw-metodista. Metodi tarkistaa, tuliko voittoja, kokamalla dice_data-dictistä kunkin nopan arvot
        dice_values-listaan, jossa noppien arvoja tutkitaan suuruusjärjestykseen perustuen. Jos voittoja tuli, metodi suorittaa voitonmaksun pelaajan pelivarauksiin
        ja kirjoittaa voittoilmoituksen infoboxiin. Muussa tapauksessa metodi toivottaa käyttäjälle parempaa onnea seuraavaan peliin.
        """

        self.__info_box.configure(text="YOU WON!")
        dice_values = []

        for dice in self.__dice_data:
            dice_values.append(self.__dice_data[dice][0])

        dice_values.sort()

        if dice_values[0] == dice_values[1] == dice_values[2] == dice_values[3] == dice_values[4]:
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Five of a kind']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT FIVE OF A KIND! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__credits_label.configure(text=self.__credits_value)
                self.__info_box.configure(text=f"YOU GOT FIVE OF A KIND! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Five of a kind']):.2f}!")


        elif (dice_values[0] == dice_values[1] == dice_values[2] == dice_values[3]
              or dice_values[1] == dice_values[2] == dice_values[3] == dice_values[4]):
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Four of a kind']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT FOUR OF A KIND! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT FOUR OF A KIND! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Four of a kind']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)


        elif ((dice_values[0] == dice_values[1] == dice_values[2] and dice_values[3] == dice_values[4]) or
              (dice_values[0] == dice_values[1] and dice_values[2] == dice_values[3] == dice_values[4])):
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Full house']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT FULL HOUSE! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT FULL HOUSE! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Full house']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)

        elif dice_values[0] == 2 and dice_values[1] == 3 and dice_values[2] == 4 and dice_values[3] == 5 and dice_values[4] == 6:
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['High straight']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT HIGH STRAIGHT! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT HIGH STRAIGHT! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['High straight']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)


        elif dice_values[0] == 1 and dice_values[1] == 2 and dice_values[2] == 3 and dice_values[3] == 4 and dice_values[4] == 5:
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Low straight']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT LOW STRAIGHT! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT LOW STRAIGHT! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Low straight']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)


        elif (dice_values[0] == dice_values[1] == dice_values[2] or dice_values[1] == dice_values[2] == dice_values[3] or
            dice_values[2] == dice_values[3] == dice_values[4]):
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Three of a kind']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT THREE OF A KIND! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT THREE OF A KIND! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Three of a kind']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)

        elif ((dice_values[0] == dice_values[1] and dice_values[2] == dice_values[3]) or (dice_values[0] == dice_values[1] and
            dice_values[3] == dice_values[4]) or (dice_values[1] == dice_values[2] and dice_values[3] == dice_values[4])):
            self.__credits_value += self.__bet_value * PAYOUT_RATIOS['Two pair']
            if self.max_credits():
                self.__info_box.configure(text="YOU GOT TWO PAIR! NOW YOU HAVE MAX CREDITS!")
            else:
                self.__info_box.configure(text=f"YOU GOT TWO PAIR! YOU WIN {(self.__bet_value * PAYOUT_RATIOS['Two pair']):.2f}!")
                self.__credits_label.configure(text=self.__credits_value)


        else:
            self.__info_box.configure(text=f"NO WIN. BETTER LUCK NEXT TIME!")


    def max_credits(self):
        """
        Metodin avulla pidetään huolta siitä, ettei pelivarausten maksimiarvo ylity. Syynä maksimiarvon asettamiselle on se, ettei pelattavuuden kannalta yli tuhannen
        pelivarauksia tarvita mihinkään ja jokin maksimiarvo täytyy asettaa jo senkin takia, ettei äärettömän pitkä luku mahdu credits_labeliin. Kun pelivaraukset
        ylittävät arvon 1000, ne palutetaan tasan tuhanteen. Tämän jälkeen pelaajalle tehdään ilmoitus siitä, että pelivaraukset eivät voi ylittää tuhatta. Ilmoitusta
        ei kuitenkaan suoriteta tässä metodissa, vaan joko metodissa insert_credits tai check_winnings, joista tätä metodia kutsutaan. Tälle syynä on se, että eri tilnteissa
        ilmoituksen kirjoitusasu on erilainen. Metodi palauttaa joko totuusarvot True tai False riippuen siitä, pyrittiinkö pelivarausten maksimiarvo ylittämään vai ei.
        """
        if self.__credits_value > 1000:
            self.__credits_value = 1000
            self.__credits_label.configure(text=f"{self.__credits_value:.2f}", bg="black", fg="white")
            self.__insert_credits_entry.delete(0, END)
            return True

        else:
            return False

    def reset(self):
        """
        Metodi nollaa atribuuttien arvot sopiviksi seuraavaa peliä varten.
        """
        self.__throw_counter = 0

        self.__dice_data[self.__dice_1][2] = False
        self.__dice_data[self.__dice_1][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(self.__dice_1))
        self.__dice_data[self.__dice_2][2] = False
        self.__dice_data[self.__dice_2][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(self.__dice_2))
        self.__dice_data[self.__dice_3][2] = False
        self.__dice_data[self.__dice_3][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(self.__dice_3))
        self.__dice_data[self.__dice_4][2] = False
        self.__dice_data[self.__dice_4][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(self.__dice_4))
        self.__dice_data[self.__dice_5][2] = False
        self.__dice_data[self.__dice_5][1].configure(text="HOLD", bg="red", fg="black", command=lambda: self.hold_dice(self.__dice_5))

    def start(self):
        """
        Metodia kutsutaan main-funktiosta ja sen ainoa toiminto on käynnistää peli.
        """
        self.__main_window.mainloop()

    def quit(self):
        """
        Metodia kutsutaan painamalla CLOSE-nappia, jolloin ohjelman suoritus lopetetaan ja pelaaminen päättyy.

        """
        self.__main_window.destroy()


def main():

    game = Dice_game()
    game.start()

if __name__ == "__main__":
    main()

