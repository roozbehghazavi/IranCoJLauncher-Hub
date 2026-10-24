TraceDef()
{
	LifeTime()
	{
		keyf(0, 60)
	}

	Size()
	{
		randf(0, 10,50 )
	}

	MaxNumTraces(50)

	Color()
	{
		keyv4(0,  1.0,1.0,1.0, 1.0)
		keyv4(0.1,1.0,1.0,0.6, 1.0)
		keyv4(9,  1.0,1.0,0.0, 1.0)
		keyv4(60, 1.0,1.0,0.0, 0.0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("WeaponHitBloodTraces.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}

