<?php

declare(strict_types=1);

function addNumbers(int $firstNumber, int $secondNumber): int
{
    return $firstNumber + $secondNumber;
}

// Example using command-line arguments
if (isset($argv[1]) && isset($argv[2])) {
    $numberOne = (int)$argv[1];
    $numberTwo = (int)$argv[2];
    $result = addNumbers($numberOne, $numberTwo);
    echo "Addition Result: " . $result . PHP_EOL;
} else {
    echo "Usage: php calculator.php <number1> <number2>" . PHP_EOL;
}
