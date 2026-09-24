Rows: 100 | categories: 29 | GBP→INR rate: 105.50


## where_order_limit
SQL: SELECT title, price_gbp, rating FROM books WHERE in_stock = 1 ORDER BY rating DESC, price_gbp DESC LIMIT 10
                                                              title  price_gbp  rating
                              Sapiens: A Brief History of Humankind      54.23       5
            Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)      52.29       5
                                       We Love You, Charlie Freeman      50.27       5
                                        Private Paris (Private #10)      47.61       5
            Worlds Elsewhere: Journeys Around Shakespeareâs Globe      40.30       5
                                                               Join      35.67       5
                                          Rip it Up and Start Again      35.02       5
                                                         Black Dust      34.53       5
The Activist's Tao Te Ching: Ancient Advice for a Modern Revolution      32.24       5
                                         Chase Me (Paris Nights #2)      25.27       5


## distinct_categories
SQL: SELECT DISTINCT category_name FROM categories ORDER BY category_name
     category_name
     Add a comment
               Art
          Business
         Childrens
      Contemporary
           Default
           Fantasy
           Fiction
    Food and Drink
            Health
Historical Fiction
           History
            Horror
             Music
           Mystery
         New Adult
        Nonfiction
        Philosophy
            Poetry
          Politics
           Romance
           Science
   Science Fiction
         Self Help
    Sequential Art
      Spirituality
          Thriller
            Travel
       Young Adult


## rating_between
SQL: SELECT title, rating FROM books WHERE rating BETWEEN 4 AND 5 ORDER BY rating DESC, title LIMIT 10
                                                                            title  rating
               #HigherSelfie: Wake Up Your Life. Free Your Soul. Find Your Tribe.       5
                                                                       Black Dust       5
                                                       Chase Me (Paris Nights #2)       5
                                                                             Join       5
                                 Princess Between Worlds (Wide-Awake Princess #5)       5
Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1)       5
                                                      Private Paris (Private #10)       5
                                                        Rip it Up and Start Again       5
                                            Sapiens: A Brief History of Humankind       5
                          Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)       5


## category_in
SQL: SELECT title, category_name FROM books JOIN categories USING(category_id) WHERE category_name IN ('Travel', 'Mystery', 'Historical Fiction') ORDER BY category_name, title LIMIT 15
                  title      category_name
     Tipping the Velvet Historical Fiction
   In a Dark, Dark Wood            Mystery
          Sharp Objects            Mystery
    The Past Never Ends            Mystery
It's Only the Himalayas             Travel


## join_top_books
SQL: SELECT c.category_name, b.title, b.rating, b.price_gbp FROM books b JOIN categories c USING(category_id) ORDER BY c.category_name, b.rating DESC, b.price_gbp DESC, b.title LIMIT 20
category_name                                                                                                                                                  title  rating  price_gbp
Add a comment The Mindfulness and Acceptance Workbook for Anxiety: A Guide to Breaking Free from Anxiety, Phobias, and Worry Using Acceptance and Commitment Therapy       4      23.89
Add a comment                                                                                                                                         The Art Forger       3      40.76
Add a comment                                                                                                                                    On a Midnight Clear       3      14.07
Add a comment                                                                                  Judo: Seven Steps to Black Belt (an Introductory Guide for Beginners)       2      53.90
Add a comment                                                                                                            The Torch Is Passed: A Harding Family Story       1      19.09
          Art                                                                                                                                         Wall and Piece       4      44.18
     Business                                                                                                     The Dirty Little Secrets of Getting Your Dream Job       4      33.34
    Childrens                                                                                                                          Birdsong: A Story in Pictures       3      54.64
    Childrens                                                                                                                        The Secret of Dreadwillow Carse       1      56.13
    Childrens                                                                                                                                 The Bear and the Piano       1      36.89
 Contemporary                                                                                                                                       When We Collided       1      31.77
      Default                                                                     The Inefficiency Assassin: Time Management Tactics for Working Smarter, Not Longer       5      20.59
      Default                                                         The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics       4      22.60
      Default                                                                                                                         Aladdin and His Wonderful Lamp       3      53.13
      Default                                                                                                                                            Penny Maybe       3      33.29
      Default                                            America's Cradle of Quarterbacks: Western Pennsylvania's Football Factory from Johnny Unitas to Joe Montana       3      22.50
      Default                                                                The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull       3      17.93
      Default                                                                                                                                            Soul Reader       2      39.58
      Default                                                                                                         Maude (1883-1993):She Grew Up with the country       2      18.02
      Default                                                                                                         Starving Hearts (Triangular Trade Trilogy, #1)       2      13.99


## Join equivalence (SQL / pandas merge)

Equivalent: True

SQL result:
     category                                                                                                                                                  title  rating  price_gbp
Add a comment The Mindfulness and Acceptance Workbook for Anxiety: A Guide to Breaking Free from Anxiety, Phobias, and Worry Using Acceptance and Commitment Therapy       4      23.89
Add a comment                                                                                                                                         The Art Forger       3      40.76
Add a comment                                                                                                                                    On a Midnight Clear       3      14.07
Add a comment                                                                                  Judo: Seven Steps to Black Belt (an Introductory Guide for Beginners)       2      53.90
Add a comment                                                                                                            The Torch Is Passed: A Harding Family Story       1      19.09
          Art                                                                                                                                         Wall and Piece       4      44.18
     Business                                                                                                     The Dirty Little Secrets of Getting Your Dream Job       4      33.34
    Childrens                                                                                                                          Birdsong: A Story in Pictures       3      54.64
    Childrens                                                                                                                        The Secret of Dreadwillow Carse       1      56.13
    Childrens                                                                                                                                 The Bear and the Piano       1      36.89
 Contemporary                                                                                                                                       When We Collided       1      31.77
      Default                                                                     The Inefficiency Assassin: Time Management Tactics for Working Smarter, Not Longer       5      20.59
      Default                                                         The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics       4      22.60
      Default                                                                                                                         Aladdin and His Wonderful Lamp       3      53.13
      Default                                                                                                                                            Penny Maybe       3      33.29
      Default                                            America's Cradle of Quarterbacks: Western Pennsylvania's Football Factory from Johnny Unitas to Joe Montana       3      22.50
      Default                                                                The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull       3      17.93
      Default                                                                                                                                            Soul Reader       2      39.58
      Default                                                                                                         Maude (1883-1993):She Grew Up with the country       2      18.02
      Default                                                                                                         Starving Hearts (Triangular Trade Trilogy, #1)       2      13.99

pandas merge result:
     category                                                                                                                                                  title  rating  price_gbp
Add a comment The Mindfulness and Acceptance Workbook for Anxiety: A Guide to Breaking Free from Anxiety, Phobias, and Worry Using Acceptance and Commitment Therapy       4      23.89
Add a comment                                                                                                                                         The Art Forger       3      40.76
Add a comment                                                                                                                                    On a Midnight Clear       3      14.07
Add a comment                                                                                  Judo: Seven Steps to Black Belt (an Introductory Guide for Beginners)       2      53.90
Add a comment                                                                                                            The Torch Is Passed: A Harding Family Story       1      19.09
          Art                                                                                                                                         Wall and Piece       4      44.18
     Business                                                                                                     The Dirty Little Secrets of Getting Your Dream Job       4      33.34
    Childrens                                                                                                                          Birdsong: A Story in Pictures       3      54.64
    Childrens                                                                                                                        The Secret of Dreadwillow Carse       1      56.13
    Childrens                                                                                                                                 The Bear and the Piano       1      36.89
 Contemporary                                                                                                                                       When We Collided       1      31.77
      Default                                                                     The Inefficiency Assassin: Time Management Tactics for Working Smarter, Not Longer       5      20.59
      Default                                                         The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics       4      22.60
      Default                                                                                                                         Aladdin and His Wonderful Lamp       3      53.13
      Default                                                                                                                                            Penny Maybe       3      33.29
      Default                                            America's Cradle of Quarterbacks: Western Pennsylvania's Football Factory from Johnny Unitas to Joe Montana       3      22.50
      Default                                                                The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull       3      17.93
      Default                                                                                                                                            Soul Reader       2      39.58
      Default                                                                                                         Maude (1883-1993):She Grew Up with the country       2      18.02
      Default                                                                                                         Starving Hearts (Triangular Trade Trilogy, #1)       2      13.99