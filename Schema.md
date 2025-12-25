## Users
{
  _id,
  name,
  email,
  password_hash,
  created_at
}

## Dataset
{
  _id,
  invoice_type,
  date,
  item,
  quantity,
  sales_price,
  amount,
  balance
}

## Models
{
  _id,
  model_name,
  version,
  model_binary,
  trained_at
}

## Predictions
{
  _id,
  user_id,
  input_data,
  prediction,
  model_version,
  created_at
}
