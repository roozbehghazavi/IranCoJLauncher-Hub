ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GravityMul()
	{
		keyf(0, 1.7)
	}

	Drag()
	{
		keyf(0, 0.6)
	}

	WindInfluence()
	{
		keyf(0, 0)
	}

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(1.6, 1, 1, 1, 1)
		keyv4(2, 1, 1, 1, 0)
	}

	Size()
	{
		randf(0, 18, 32)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_DebrisWood_particleBLEND.mat", "IRN_DebrisWood_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
