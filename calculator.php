<?php

declare(strict_types=1);

/**
 * Simple calculator program
 */

function addNumbers(int $firstNumber, int $secondNumber): int
{
    return $firstNumber + $secondNumber;
}

$numberOne = 10;
$numberTwo = 20;

$result = addNumbers($numberOne, $numberTwo);

echo "Addition Result: " . $result . PHP_EOL;
