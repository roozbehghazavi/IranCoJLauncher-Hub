TraceDef()
{
	LifeTime()
	{
		keyf(0, 340)
	}

	Size()
	{
		randf(0, 10, 24)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	MaxNumTraces(240)

	Color()
	{
		keyv4(0,  1.0,1.0,0.5, 0.5)
		keyv4(2,  1.0,1.0,0.0, 0.5)
		keyv4(30, 1.0,1.0,0.0, 0.0)
	}

	Material("BloodWaterTraces.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
