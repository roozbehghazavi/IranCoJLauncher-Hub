ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.6)
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
		keyv4(0, 0.45, 0.45, 0.45, 0.02)
		keyv4(0.02, 0.45, 0.45, 0.45, 0.13)
		keyv4(0.35, 0.45, 0.45, 0.45, 0.08)
		keyv4(0.6, 0.45, 0.45, 0.45, 0)
	}

	Size()
	{
		randf(0, 80, 115)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodMist_particleBLEND.mat", "IRN_BloodMist_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
