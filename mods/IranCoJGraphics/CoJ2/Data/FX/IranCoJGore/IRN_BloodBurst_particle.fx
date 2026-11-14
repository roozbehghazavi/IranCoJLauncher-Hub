ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.3)
	}

	GravityMul()
	{
		randf(0, 1.6, 1.8)
	}

	Drag()
	{
		randf(0, 9, 10)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 0.5)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.43)
		keyv4(0.272, 0.55, 0.55, 0.55, 0.25)
		keyv4(0.78, 0.55, 0.55, 0.55, 0.06)
		keyv4(1.3, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 34)
		keyf(1.3, 62)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodBurst_particleBLEND.mat", "IRN_BloodBurst_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
