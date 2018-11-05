var x_A integer;
var x_B integer;
maximize Profit : 25*x_A + 30*x_B;
subject to Time : (1/200)*x_A + (1/140)*x_B <= 40;
subject to A_limit : 0 <= x_A <= 6000;
subject to B_limit : 0 <= x_B <= 4000;