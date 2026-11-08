TraceDef()
{
	LifeTime()
	{
		keyf(0, 60)
	}

	Size()
	{
	    randf(0, 8, 10)
	}

	MaxNumTraces(50)

	Color()
	{
		keyv4(0,  1.0,1.0,1.0, 1.0)
		keyv4(0.1,1.0,1.0,0.6, 1.0)
		keyv4(9,  1.0,1.0,0.0, 1.0)
		keyv4(60, 1.0,1.0,0.0, 0.0)
	}

	Material("Wound_particleMUL.mat")
}
