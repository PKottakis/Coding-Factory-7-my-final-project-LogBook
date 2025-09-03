# Generated manually for renaming meters to Band

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0004_remove_station_decoding_ft8_ft4_cw_etc_station_cw_and_more'),
    ]

    operations = [
        # Rename the model from meters to Band
        migrations.RenameModel(
            old_name='meters',
            new_name='Band',
        ),
        # Rename the field from meters to band in Station model
        migrations.RenameField(
            model_name='station',
            old_name='meters',
            new_name='band',
        ),
        # Update the ForeignKey reference
        migrations.AlterField(
            model_name='station',
            name='band',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Station', to='station.band'),
        ),
    ] 