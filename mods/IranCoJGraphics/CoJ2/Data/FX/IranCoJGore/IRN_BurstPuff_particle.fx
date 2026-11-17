ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.7)
	}

	GravityMul()
	{
		randf(0, 0, 0)
	}

	Drag()
	{
		randf(0, 5, 10)
	}

	Color()
	{
		keyv4(0, 0.45, 0.45, 0.45, 0.17)
		keyv4(0.03, 0.45, 0.45, 0.45, 0.36)
		keyv4(0.39, 0.45, 0.45, 0.45, 0.39)
		keyv4(0.7, 0.45, 0.45, 0.45, 0)
	}

	Size()
	{
		randf(0, 36, 50)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodMist_particleBLEND.mat", "IRN_BloodMist_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
