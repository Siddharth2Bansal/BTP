known bugs:
~~combiner secret not same~~
~~some other issue also related to not being in Z_p*~~
~~reconstruction not working well~~

left out:
proper hash functions
~~verification of pseudo shares~~
~~combiner verification phase~~
~~transfer of pseudo shares to combiner~~
~~need to set up debugger~~
pseudo share verification by combiner
~~lagrange interpolation somehow not giving correct answers, need to test with dry runs need to check the function "f" for zero values~~
Security analysis
~~separation of code into the different entities~~
    ~~currently working on~~
~~socket programming and separating code into different classes~~
currently infinitely pinging the board every 5 seconds on failed requests,  need to keep a threshold here for cases with information withholding.
need to add method for bulletin to turn off at the end
need to run cases with varied k and t values
stronger values for the curve and the prime numbers

Questions:
1.
# should i implement combiner secret verification???
# only mentioned offhandly in the paper

2.
# i dont see the point of combiner verification
# the sharing process will anyways only allow the verified combiner to access the shares

3. 
# Third security threat does not look possible to be implemented

quirks:
1. not storing the curve details in the bulletin board as sharing tinyec elements over board is not fesible and saving curve implementation in the board is unnecessary.
2. sharing the points over the network is done as (x, y) pairs instead of the point class, due to the difficulty with sending tinyec elements.



Security Analysis:
1. Make the dealer use incorrect X_i value for one participant.
2. Make participant transmit incorrect X_i value to combiner.
3. Add extra participant and try to use it to submit the pseudo share(idk actually, ask).
4. Collusion cannot occur and should not need to be implemented to be shown.
5. Make combiner verification from an extra third party and show its invalid.
6. ECDLP based thing.
7. ECDLP again.
8. And again.
9. run twice and show that only changing random seed will affect thing greatly.
10. Property of Bulletin Board.
11. I really dont think this needs to be checked.