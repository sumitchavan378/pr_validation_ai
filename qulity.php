<?php

// bad naming, no strict types, no comments
function calc($a,$b){
    $result = 0;

    // unnecessary loop
    for($i=0;$i<1;$i++){
        $result = $a + $b;
    }

    // debug print left in code
    echo "Result is: ".$result;

    return $result;
}

// hardcoded values, no validation
$x = $_GET['x'];
$y = $_GET['y'];

if($x && $y){
    calc($x,$y);
}else{
    echo "missing input";
}

// unused variable
$unused = 123;

// duplicate logic
function calc2($a,$b){
    return $a + $b;
}
