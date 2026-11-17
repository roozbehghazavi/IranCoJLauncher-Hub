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
		randf(0, 10, 15)
	}

	Color()
	{
		keyv4(0, 0.45, 0.45, 0.45, 0.015)
		keyv4(0.012, 0.45, 0.45, 0.45, 0.12)
		keyv4(0.4, 0.45, 0.45, 0.45, 0.074)
		keyv4(0.7, 0.45, 0.45, 0.45, 0)
	}

	Size()
	{
		randf(0, 100, 140)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodMist_particleBLEND.mat", "IRN_BloodMist_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
