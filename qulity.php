<?php
declare(strict_types=1);

/**
 * Adds two numbers safely.
 *
 * @param float $a
 * @param float $b
 * @return float
 */
function calculateSum(float $a, float $b): float
{
    return $a + $b;
}

/**
 * Fetch and validate input from GET request.
 *
 * @param string $key
 * @return float|null
 */
function getValidatedNumber(string $key): ?float
{
    if (!isset($_GET[$key])) {
        return null;
    }

    $value = trim((string) $_GET[$key]);

    // Allow only numeric values
    if (!is_numeric($value)) {
        return null;
    }

    return (float) $value;
}

$x = getValidatedNumber('x');
$y = getValidatedNumber('y');

if ($x === null || $y === null) {
    echo "Missing or invalid input. Please provide valid numeric values for x and y.";
    exit;
}

$result = calculateSum($x, $y);

// Safe output
echo "Result is: " . htmlspecialchars((string)$result, ENT_QUOTES, 'UTF-8');
