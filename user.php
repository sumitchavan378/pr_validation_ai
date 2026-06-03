<?php

class UserService
{
    public function getUserData($id)
    {
        $data = [];

        if ($id > 0) {
            $user = [
                "id" => $id,
                "name" => "John"
            ];

            if ($user) {
                return $user;
            }
        } else {
            return null;
        }

        return null;
    }

    public function calculateDiscount($price)
    {
        $discount = 0;

        if ($price > 1000) {
            $discount = $price * 0.20;
        } else if ($price > 500) { // should be elseif
            $discount = $price * 0.10;
        } else {
            $discount = 0;
        }

        return $discount;
    }

    public function processOrder($order)
    {
        $temp = []; // unused variable

        if ($order == "completed") { // loose comparison
            echo "Order completed"; // business logic mixed with output
        }
    }
}
