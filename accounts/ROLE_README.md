Initialize default roles and permissions

Run the management command to create three groups and assign permissions:

    python manage.py init_roles [--assign-manager] [--assign-owner]

- `--assign-manager` will give the Manager group any permissions belonging to the `accounts` app (example behavior).
- `--assign-owner` will give the Property owner group any permissions belonging to the `accounts` app (example behavior).

After running, visit the Django admin (Users & Groups) to review and fine-tune permissions per group.

Create a demo admin user (development only)

You can create or update a demo admin user for local development with:

    python manage.py create_demo_admin --username admin --email admin@example.com --password AdminPass123!

This will create or update a superuser with staff privileges. Do NOT use this in production; change credentials or remove the user before deploying.

Create demo Property manager and Property owner users

To create two demo users for testing:

    python manage.py create_demo_users

Defaults created:

- Property manager: username `pmanager`, password `UserPass123!`
- Property owner: username `powner`, password `UserPass123!`

You can override via flags shown in the command help.
