param constrK, integer, > 0;
param taskN, integer, > 0;

set iterK := 1..constrK;
set iterN := 1..taskN;

# old cstr
param nJob {k in iterK, i in iterN}, >= 0;
param tk {k in iterK}, >= 0;

# new cstr (that we want to check for redundancy)
param nJobNew {i in iterN}, >= 0;
param tkNew, >= 0;

var C {i in iterN}, integer, >= 1;

maximize newCstr: sum{i in iterN} C[i] * nJobNew[i];

s.t.
cstr{k in iterK} : sum{i in iterN} C[i] * nJob[k,i] <= tk[k];  # oldCstr
cstr_2 : sum{i in iterN} C[i] * nJobNew[i] <= tkNew + 1;  # bound for the objective function

solve;

# printf{i in iterN} "C[%d] = %d\n", i, C[i];
# printf "sol: %d < %d\n", newCstr, tkNew;

display sum{i in iterN} C[i] * nJobNew[i];

end;

