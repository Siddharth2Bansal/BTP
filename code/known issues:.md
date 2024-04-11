known bugs:
~~combiner secret not same~~
~~some other issue also related to not being in Z_p*~~
~~reconstruction not working well~~

left out:
proper hash functions
~~verification of pseudo shares~~
combiner verification phase
~~transfer of pseudo shares to combiner~~
~~need to set up debugger~~
pseudo share verification by combiner
~~lagrange interpolation somehow not giving correct answers, need to test with dry runs need to check the function "f" for zero values~~
Security analysis
separation of code into the different entities
    currently working on
socket programming and separating code into different classes


Questions:
1.
# should i implement combiner ecret verification???
# only mentioned offhandly in the paper

2.
# i dont see the point of combiner verification
# the sharing process will anyways only allow the verified combiner to access the shares


quirks:
1. not storing the curve details in the bulletin board as sharing tinyec elements over board is not fesible and saving curve implementation in the board is unnecessary.
2. sharing the points over the network is done as (x, y) pairs instead of the point class, due to the difficulty with sending tinyec elements.