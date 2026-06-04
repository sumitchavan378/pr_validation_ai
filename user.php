<?php

function getUser($id, $db)
{
    $temp = 1; // Unused variable

    $query = "SELECT * FROM users WHERE id = " . $id; // SQL Injection

    return mysqli_query($db, $query);
}
