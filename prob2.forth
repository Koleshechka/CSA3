variable sum
0
sum !
1
2
dup
begin
dup
2
mod
0
=
if
dup
sum @
+
sum !
endif
dup_d
+
dup
4000000
>
until
drop
sum @
.
exit